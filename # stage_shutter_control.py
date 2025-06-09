# stage_shutter_control.py
# 研究用ステージおよびシャッター制御スクリプト
# author: [あなたの名前 or GitHubユーザー名（任意）]
# last update: 2024-06-XX

import serial
import time

# ==== シリアルポート設定 ====
Stage_COM_PORT = "COM3"  # ステージ制御用ポート
Shutter_COM_PORT = "COM4"  # シャッター制御用ポート

# ==== コマンドリスト定義 ====
# 各コマンド: (コマンド文字列, ポート, 待機秒数)
commands = [
    # ステージ初期設定
    ("AXIs1:UNIT MM:AXIs2:UNIT MM", Stage_COM_PORT, 0.5),
    ("AXIs1:STANDARD 0.001:AXIs2:STANDARD 0.001", Stage_COM_PORT, 0.5),
    ("AXIs1:DRDIV 0:AXIs2:DRDIV 0", Stage_COM_PORT, 0.5),
    ("AXIs1:MEMSWO 3:AXIs2:MEMSWO 3", Stage_COM_PORT, 0.5),
    # 原点復帰
    ("AXIsALL:GO ORG", Stage_COM_PORT, 30),
    # ステージ位置制御＋シャッター操作シーケンス
    ("AXIs1:SELSP 3:GOABS -10", Stage_COM_PORT, 20),
    ("AXIs2:SELSP 3:GOABS -10", Stage_COM_PORT, 20),
    ("OPEN:1", Shutter_COM_PORT, 4),
    ("AXIs2:SELSP 3:GOABS 10", Stage_COM_PORT, 35),
    ("AXIs2:SELSP 3:GOABS -10", Stage_COM_PORT, 35),
    ("AXIs2:SELSP 3:GOABS 10", Stage_COM_PORT, 35),
    ("CLOSE:1", Shutter_COM_PORT, 4),
    ("AXIs1:SELSP 3:GOABS -9.89", Stage_COM_PORT, 4),
    ("OPEN:1", Shutter_COM_PORT, 35),
    ("AXIs2:SELSP 3:GOABS -10", Stage_COM_PORT, 35),
    ("AXIs2:SELSP 3:GOABS 10", Stage_COM_PORT, 35),
    ("AXIs2:SELSP 3:GOABS -10", Stage_COM_PORT, 4),
    ("CLOSE:1", Shutter_COM_PORT, 35),
    ("AXIs1:SELSP 3:GOABS -9.78", Stage_COM_PORT, 4),
]

# ==== 繰り返し回数 ====
repeat_count = 91  # ステージ繰り返し回数
INITIAL_AX1_VALUE = -9.67  # AX1の初期位置

# ==== コマンド実行関数 ====
def execute_command(cmd, port, wait_time, ax1_value=None):
    """1つのコマンドをシリアル経由で実行"""
    try:
        with serial.Serial(port, 9600, timeout=3) as ser:
            print(f"Executing command: {cmd}")
            ser.write(f"{cmd}\r\n".encode())  
            time.sleep(wait_time)  
            if ser.in_waiting > 0:
                response = ser.readline().decode().strip()
                print(f"Received: {response}")
    except serial.SerialException as e:
        print(f"Serial error on port {port}: {e}")

    return ax1_value + 0.11 if ax1_value is not None else ax1_value 

# ==== メイン処理 ====
def main():
    # 初期コマンドの実行
    for cmd, port, wait_time in commands:
        execute_command(cmd, port, wait_time)

    # 繰り返し動作
    ax1_value = INITIAL_AX1_VALUE
    for loop_idx in range(repeat_count):
        print(f"\n--- Loop {loop_idx + 1}/{repeat_count} ---")
        for i in range(7, 19):  # コマンドリストの一部をループで実行
            cmd, port, wait_time = commands[i]
            if i == 12 or i == 18:  # AX1位置変更
                cmd = f"AXIs1:SELSP 3:GOABS {ax1_value:.3f}"
            ax1_value = execute_command(cmd, port, wait_time, ax1_value)

    print("Sequence complete. Waiting before close...")
    time.sleep(4)

# ==== 実行エントリポイント ====
if __name__ == "__main__":
    main()
    print("Serial connection closed.")
