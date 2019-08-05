# -*- coding: utf-8 -*-
import nfc
import binascii
import datetime
import sys
import time
import pymysql.cursors

#DB用リーダーの識別名
Device = "test"

def db_connect():
	global conn, cursor
	try:
		conn = pymysql.connect(host="13.112.115.196", user="health01", password="felicahealth01", db="felica_health", charset="utf8")
		cursor = conn.cursor()
	except pymysql.err.OperationalError:
		print("ネットワーク接続失敗！接続状況を確認して下さい")
		go_to_exit()

def on_connect(tag):
	global send_menu
	Timestamp = datetime.datetime.today()
	ID = binascii.hexlify(tag.identifier).upper().decode()
	PMM = binascii.hexlify(tag.pmm).upper().decode()
	SYS = hex(tag.sys)[2:].upper()
	print("ID: %s" % ID)
	print("PMM: %s" % PMM)
	print("SYS: %s" % SYS)
	try:
		cursor.execute("SELECT * from card_id where ID='%s' and PMM='%s' and SYS='%s'" % (ID,PMM,SYS))
		table = cursor.fetchall()
	except pymysql.err.OperationalError:
		print("データベース接続失敗")
		go_to_exit()

	if table == ():
		cursor.execute("INSERT INTO card_id (ID, PMM, SYS) value (\"%s\",\"%s\",\"%s\")" % (ID,PMM,SYS))
		conn.commit()
		print("データベース新規登録中")

	else:
		print ("データベースに登録済み")

	# 購入履歴の送信
	for arg in send_menu:
		cursor.execute("INSERT INTO history (Timestamp, ID, PMM, SYS, menuname, price ,kcal) value (\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%d\",\"%f\")" % (str(Timestamp),ID,PMM,SYS,arg[1],arg[2],arg[3]))
		conn.commit()

def show_menu():
	try:
		cursor.execute("SELECT * from menu")
		table = cursor.fetchall()
	except pymysql.err.OperationalError:
		print("データベース接続失敗")
		led_error()
		table = "NW error"

	if table == ():
		print("メニューが登録されていません")
	elif table == "NW error":
		print("ネットワークエラーのためメニュー読み込み失敗")
	else:
		# print(table)
		return table

def felica():
	try:
		clf = nfc.ContactlessFrontend("usb")
	except IOError:
		print("リーダーが接続されていません")
		go_to_exit()

	rdwr_options = {
		'targets': ['212F' , '424F'],
		'on-connect': on_connect,
		#'iterations': 1,
		#'interval': 0.2,
	}
	try:
		clf.connect(rdwr=rdwr_options)
	except KeyboardInterrupt:
		go_to_exit()

	sys.exit()

def go_to_exit():
	print("終了処理中")
	sys.exit()

def main():
	global send_menu
	menu = show_menu()
	while True:
		maxindex = 0
		print("##########################")
		for arg in menu:
			print("番号: %s メニュー名: %s 価格: %s円 カロリー: %skcal" % (arg[0],arg[1],arg[2],arg[3]))
			maxindex = int(arg[0])
		print("##########################")

		select = input("番号を選択(複数可能)>>> ").split(",")
		selectnum = ()
		for arg in select:
			try:
				if(int(arg) <= maxindex):
					selectnum += (int(arg),)
				else:
					print("メニューにない番号が入力されました。正しい番号を入力してください。")
			except ValueError:
				print("番号以外の文字が入力されました。正しく入力してください。")
			except IndexError:
				print("メニューにない番号が入力されました。正しい番号を入力してください。")

		total_price = 0
		total_kcal = 0
		send_menu = ()
		print("選択されたメニュー:")
		print("----------------")
		for arg in selectnum:
			print("%s %s %s円 %skcal" % (menu[arg-1][0],menu[arg-1][1],menu[arg-1][2],menu[arg-1][3]))
			total_price += menu[arg-1][2]
			total_kcal += menu[arg-1][3]
			send_menu += (menu[arg-1],)

		if total_price != 0 and total_kcal != 0:
			# print ("---data---")
			# print(send_menu)
			print("----------------")
			print("合計金額: %s円" % total_price)
			print("合計カロリー: %skcal" % total_kcal)
			while True:
				payment = input("お支払いへ進むにはY、選択に戻るにはNを入力してください>>> ")
				if payment == "Y" or payment == "y":
					print("お支払いに進みます")
					felica()
					break
				elif payment == "N" or payment == "n":
					print("メニューに戻ります")
					break
				else:
					print("正しく入力してください")
		else:
			print("Empty")
			print("メニューに戻ります")

if __name__ == '__main__':
	db_connect()
	main()