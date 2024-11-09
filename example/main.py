from pygui import AppContext, Activity, ButtonView, LinearLayout, View
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

class CustomView(View):
    def __init__(self, context):
        super().__init__(context)

    def OnMeasure(self, wSpec, hSpec):
        self.SetMeasuredDimension(50, 50)

    def Draw(self, surface):
        self.FillSelf(surface, (128, 0, 128))
        self.DrawLine(surface, (128, 255, 0), (1, 1), (self.Rect.width - 2, self.Rect.height - 2), 2)
        self.DrawRect(surface, (255, 255, 0), (0, 0, self.Rect.width, self.Rect.height), 2)

class MainActivity(Activity):
    def OnInit(self):
        group = LinearLayout(self.Context)
        
        button1 = ButtonView(self.Context, 'Start OtherActivity!')
        button1.ClickAction = lambda pos, view, button: self.StartActivity("OtherActivity")

        button2 = ButtonView(self.Context, "Switch to OtherActivity!")
        button2.ClickAction = lambda pos, view, button: self.SwitchToActivity("OtherActivity")

        customView = CustomView(self.Context)

        group.AddChild(button1)
        group.AddChild(button2)
        group.AddChild(customView)

        self.SetContentView(group)
        

class OtherActivity(Activity):
    def OnInit(self):
        group = LinearLayout(self.Context)
        button1 = ButtonView(self.Context, "Start MainActivity")
        button1.ClickAction = lambda pos, view, button: self.StartActivity('MainActivity')

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

