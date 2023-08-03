from screen_capture import ScreenCapture


def run():
    # capture
    sc = ScreenCapture(template='img/template.png', score=0.65)
    sc.run()


if __name__ == '__main__':
    run()

