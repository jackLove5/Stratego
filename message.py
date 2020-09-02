"""
Message class
"""
class Message:
  def __init__(self, recipient, msg):
    self.recipient_sid = recipient
    self.message = msg
