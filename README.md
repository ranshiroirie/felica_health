# felica_health
・buylunch.py
体重計なしで購入情報のみを送信するプログラム

・buylunch-fo-raspi.py
hx711ライブラリを使用した体重計による計測と、体重と購入情報を送信するプログラム

・hx711.py
外部のライブラリを使用 (参考:https://github.com/tatobari/hx711py)
使用するにあたり、python２用であるライブラリを本プログラムではpython3で動かすため、2to3コマンドによる変換、２１９行目あたりの割り算を//に変更
