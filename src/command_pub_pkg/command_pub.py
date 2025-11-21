#!/usr/bin/env python3
# encoding: utf-8

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from .Speech_Lib import Speech


spe = Speech()

class VoiceCommandPublisher(Node):
    def __init__(self):
        super().__init__('voice_command_node')
        
        # publish topoic ：/voice_command
        self.publisher = self.create_publisher(String, '/voice_command', 10)
        
        # 100Hz
        self.timer = self.create_timer(0.1, self.timer_callback)
        
        self.get_logger().info("voice command  → topic: /voice_command")

    def timer_callback(self):
        speech_r = spe.speech_read()      # read the speech contant 
        ###发布字符串，播报内容
        # 如果没有新命令，直接返回
        if speech_r == 0:
            return
            
        
        spe.void_write(speech_r)

        # transfer ID to Chinese
        command_map = {
            1: "欢迎使用小亚",
            2: "我去休息啦",
            3: "我在",
            4: "增大音量",
            5: "减小音量",
            6: "最大音量",
            7: "中等音量",
            8: "最小音量",
            9: "开启播报",
            10: "关闭播报",
            11: "好的，已停止",
            14: "好的，正在前进",
            15: "好的，正在后退",
            16: "好的，正在向左转",
            17: "好的，正在向右转"
            # 你还可以继续加...
        }

        text = command_map.get(speech_r, f"unknow ID:{speech_r}")
        
        msg = String()
        msg.data = text
        
        self.publisher.publish(msg)
        self.get_logger().info(f"voice recognition → {text} (ID: {speech_r})")


def main(args=None):
    rclpy.init(args=args)
    node = VoiceCommandPublisher()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
