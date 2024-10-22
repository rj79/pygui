from pygui import AppContext, Activity, ButtonView, LinearLayout
import asyncio

def get_event_loop():
    import sys
    if sys.version_info < (3, 10):
        loop = asyncio.get_event_loop()
    else:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()

    asyncio.set_event_loop(loop)
    return loop


class MainActivity(Activity):
    def OnInit(self):
        group = LinearLayout(self.Context)
        
        button1 = ButtonView(self.Context, 'Start OtherActivity!')
        button1.ClickAction = lambda pos, view, button: self.StartActivity("OtherActivity")

        button2 = ButtonView(self.Context, "Switch to OtherActivity!")
        button2.ClickAction = lambda pos, view, button: self.SwitchToActivity("OtherActivity")

        group.AddChild(button1)
        group.AddChild(button2)

        self.SetContentView(group)
        

class OtherActivity(Activity):
    def OnInit(self):
        group = LinearLayout(self.Context)
        button1 = ButtonView(self.Context, "Start OtherActivity")
        button1.ClickAction = lambda pos, view, button: self.StartActivity('OtherActivity')

        button2 = ButtonView(self.Context, "Switch to MainActivity")
        button2.ClickAction = lambda pos, view, button: self.SwitchToActivity("MainActivity")
        group.AddChild(button1)
        group.AddChild(button2)
        self.SetContentView(group)


class ExampleApp(AppContext):
    def __init__(self, width, height):
        super().__init__(width, height)

        mainActivity = MainActivity(self, 'MainActivity')
        otherActivity = OtherActivity(self, "OtherActivity")

        self.RegisterActivity(mainActivity)
        self.RegisterActivity(otherActivity)

        self.StartActivity('MainActivity')
        

if __name__ == '__main__':
    import logging
    import os
    LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()
    logging.basicConfig(level=LOGLEVEL, format="%(asctime)s %(message)s")
    app = ExampleApp(800, 600)
    loop = get_event_loop()
    loop.run_until_complete(app.pygame_task())

