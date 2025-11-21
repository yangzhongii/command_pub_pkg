#!/usr/bin/env python3
# encoding: utf-8

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
# from Speech_Lib import Speech

# Global Speech instance with safety fallback
# try:
#     spe = Speech()
# except Exception as e:
#     print(f"警告：语音模块串口打开失败 → {e}")
#     spe = None
spe = None

class VoiceCommandPublisher(Node):
    def __init__(self):
        super().__init__('voice_command_node')
        global spe
        from Speech_Lib import Speech
        spe = Speech()
        self.publisher = self.create_publisher(String, '/voice_command', 10)
        self.timer = self.create_timer(0.05, self.timer_callback)  # 20 Hz

        
        self.command_map = {
            # 1:  "欢迎使用小亚",
            2:  "我去休息啦",
            3:  "好的, 已休眠",
            4:  "小车前进",
            5:  "小车后退",
            6:  "小车左转",
            7:  "小车右转",
            8:  "小车左旋",
            9:  "小车右旋",
            10: "关灯",
            11: "亮红灯",
            12: "亮绿灯",
            13: "亮蓝灯",
            14: "亮黄灯",
            15: "打开流水灯",
        
        }
        # =======================================

        self.get_logger().info("语音指令节点已启动 → 话题: /voice_command")

    def timer_callback(self):
        if spe is None:
            return

        raw_id = spe.speech_read()

        
        if raw_id in (999, 111, 0):
            return

        # 安全播报
        safe_id = raw_id & 0xFF
        spe.void_write(safe_id)

        # 查表得到中文
        text = self.command_map.get(raw_id, f"未知指令 ID:{raw_id}")

        # 发布话题
        msg = String()
        msg.data = text
        self.publisher.publish(msg)

       
        self.get_logger().info(f"语音识别 → {text} (ID: {raw_id})")


def main(args=None):
    rclpy.init(args=args)
    node = VoiceCommandPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if spe is not None:
            spe.__del__()  
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()