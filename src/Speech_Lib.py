#!/usr/bin/env python3
# coding: utf-8
# Yahboom Offline Speech Recognition Module Library (UART version)
# Protocol: AA 55 FF <ID> FB
# This version is completely safe: filters power-on 999, noise 0x6F (111), and forces all IDs into 0-255 range

import time
import serial
import os
import sys


class Speech(object):
    """
    Driver for Yahboom offline speech recognition module (UART mode, /dev/myspeech)
    """

    def __init__(self, com="/dev/myspeech", baudrate=115200, timeout=0.1):
        """
        Open serial port and ensure no other process is holding it.
        Kills lingering processes (common in ROS2 when nodes are killed improperly).
        """
        # Force-kill any process still occupying the serial port
        os.system(f"sudo fuser -k {com} >/dev/null 2>&1")
        time.sleep(0.2)

        try:
            self.ser = serial.Serial(
                port=com,
                baudrate=baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=timeout
            )
            if self.ser.is_open:
                print(f"[Speech] Successfully opened {com} @ {baudrate} baud")
            else:
                print(f"[Speech] Failed to open serial port {com}")
                sys.exit(1)
        except Exception as e:
            print(f"[Speech] Cannot open {com}: {e}")
            sys.exit(1)

    def __del__(self):
        """Safely close the serial port when the object is destroyed."""
        if hasattr(self, 'ser') and self.ser and self.ser.is_open:
            self.ser.close()
            print("[Speech] Serial port closed.")

    # def void_write(self, void_data):
    #     """
    #     Send a voice playback command to the module.
    #     Parameter:
    #         void_data (int): voice entry ID (can be any number)
    #     Behaviour:
    #         - Forces the ID into one byte (0-255) using & 0xFF → prevents crash on 999/1000/etc.
    #         - Uses bytes() instead of list → safest way to send data
    #     """
    #     cmd_id = int(void_data) & 0xFF                                 # Critical safety: never exceed 255
    #     cmd = bytes([0xAA, 0x55, 0xFF, cmd_id, 0xFB])                  # Fixed protocol frame

    #     print(f"[Speech] Playback → raw ID: {void_data} → sent as: {cmd_id} | frame: {[hex(b) for b in cmd]}")

    #     try:
    #         self.ser.write(cmd)
    #         time.sleep(0.01)                                           # Module needs a short delay
    #         self.ser.flushInput()                                      # Discard echo/garbage
    #     except Exception as e:
    #         print(f"[Speech] Write failed: {e}")
    def void_write(self, void_data):
        cmd_id = int(void_data) & 0xFF
        cmd = bytes([0xAA, 0x55, 0xFF, cmd_id, 0xFB])
        print(f"[Speech] Playback → raw:{void_data} → safe:{cmd_id}")
        self.ser.write(cmd)
        time.sleep(0.01)
        self.ser.flushInput()

    # def speech_read(self):
    #     """
    #     Read one recognition result from the module.
    #     Returns:
    #         0           → no valid command (or garbage/power-on frame)
    #         1-255       → valid recognized voice entry ID
    #     Features:
    #         - Strict 5-byte frame validation (AA 55 FF xx FB)
    #         - Filters power-on/self-test frame (999)
    #         - Filters "not recognized" noise frame (0x6F = 111)
    #     """
    #     try:
    #         if self.ser.in_waiting == 0:
    #             return 0

    #         # Read all currently available bytes
    #         raw = self.ser.read(self.ser.in_waiting)
    #         hex_str = raw.hex().lower()

    #         # Must be at least one complete frame (10 hex characters = 5 bytes)
    #         if len(hex_str) < 10:
    #             return 0

    #         # Valid frame must start with aa55 and end with fb
    #         if hex_str.startswith('aa55') and hex_str.endswith('fb'):
    #             payload_hex = hex_str[6:8]                  # 4th byte = actual ID
    #             cmd_id = int(payload_hex, 16)

    #             # Ignore known garbage frames
    #             if cmd_id in (999, 111):                    # 999 = power-on, 111 = noise/not recognized
    #                 self.ser.flushInput()
    #                 return 0

    #             print(f"[Speech] Recognized valid ID: {cmd_id}")
    #             self.ser.flushInput()
    #             return cmd_id

    #     except Exception as e:
    #         print(f"[Speech] Read error: {e}")

    #     # Any error or invalid frame → treat as no command
    #     self.ser.flushInput()
    #     return 0
    def speech_read(self):
        """
        Read one recognition result from the module.
        Returns:
            0           → no valid command (including power-on 999 and noise 0x6F)
            1-255       → valid recognized voice entry ID
        This function completely filters:
            • Power-on / wake-up frame (999)
            • "Not recognized" noise frame (0x6F = 111)
        """
        try:
            if self.ser.in_waiting == 0:
                return 0

            raw = self.ser.read(self.ser.in_waiting)
            hex_str = raw.hex().lower()

            # Must be at least one complete 5-byte frame
            if len(hex_str) < 10 or not hex_str.startswith('aa55') or not hex_str.endswith('fb'):
                return 0

            # Extract the 4th byte (the actual ID)
            payload_hex = hex_str[6:8]
            cmd_id = int(payload_hex, 16)

            # ---- 永久封杀 999 和 0x6F（111） ----
            if cmd_id == 999 or cmd_id == 111:      # 999 = power-on, 111 = noise/not recognized
                self.ser.flushInput()               # 清空缓冲区，防止重复上报
                return 0                            # ← 直接吃掉，不返回给主节点

            # 正常有效指令才返回
            print(f"[Speech] Valid recognition → ID = {cmd_id}")
            self.ser.flushInput()
            return cmd_id

        except Exception as e:
            print(f"[Speech] Read exception: {e}")
            return 0