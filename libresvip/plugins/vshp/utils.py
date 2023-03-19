def ansi2unicode(content: bytes) -> str:
    try:
        return content.decode("gbk")
    except UnicodeDecodeError:
        return content.decode("shift-jis")