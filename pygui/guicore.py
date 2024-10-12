from __future__ import annotations
import asyncio
from .colors import *
from .common import Point
import logging
from os.path import join
import pygame


from time import monotonic

MATCH_PARENT = -1
WRAP_CONTENT = -2

CENTER = 0x11
CENTER_HORIZONTAL = 0x01
CENTER_VERTICAL = 0x11

def SurfaceToString(surface):
    return "(w=%d h=%d p=%d)" % (surface.get_width(),
                                 surface.get_height(),
                                 surface.get_pitch())

class Dimension:
    def __init__(self, *args):
        self.set(*args)

    def set(self, *args):
        if len(args) == 1 and isinstance(args[0], Dimension):
            self._width = args[0]._width
            self._height = args[0]._height
        elif len(args) == 1 and isinstance(args[0], tuple):
            self._width = args[0][0]
            self._height = args[0][1]            
        elif len(args) == 2:
            self._width = args[0]
            self._height = args[1]
        else:
            self._width = 0
            self._height = 0
            
    def widen(self, amount):
        if amount > 0:            
            self._width += amount

    def heigten(self, amount):
        if amount > 0:            
            self._height += amount
    
    @property
    def width(self) -> int:
        return self._width
    
    @property
    def height(self) -> int:
        return self._height
    
    def at_least(self, dimension:Dimension):
        if self._width < dimension._width:
            self._width = dimension._width
        if self._height < dimension._height:
            self._height = dimension._height

    def to_tuple(self) -> tuple[int, int]:
        return (self._width, self._height)
    
    def __repr__(self) -> str:
        return f'<Dimension {self._width}, {self._height}>'

class MeasureSpec:
    UNSPECIFIED = 1
    EXACTLY = 2
    AT_MOST = 3

    def __init__(self, mode = UNSPECIFIED, size = 0):
        self.Mode = mode
        self.Size = size

    def __repr__(self):
        if self.Mode == MeasureSpec.UNSPECIFIED:
            text = "UNSPECIFIED "
        elif self.Mode == MeasureSpec.EXACTLY:
            text = "EXACTLY "
        elif self.Mode == MeasureSpec.AT_MOST:
            text = "AT_MOST "
        else:
            text = "ERROR "

        text += str(self.Size)
        return text

    def GetSize(self):
        return self.Size

    def GetMode(self):
        return self.Mode


def args_to_point(*args):
    if len(args) == 1 and isinstance(args[0], Point):
        return args[0]
    if len(args) == 1 and isinstance(args[0], tuple):
        return Point(args[0][0], args[0][1])
    if len(args) == 2:
        return Point(args[0], args[1])


def OnClickDoNothing(pos, view:View, button:int):
    pass


def MeasureText(text, name, size, bold, italic):
    font = pygame.font.SysFont(name, size, bold, italic)
    return font.size(text)


def DrawText(surface, pos, text,
             size=12,
             name='sans',
             color=(0, 0, 0),
             bold=False,
             italic=False,
             antialias=True):
    font = pygame.font.SysFont(name, size, bold, italic)

    msgSurface = font.render(text, antialias, color)
    msgRect = msgSurface.get_rect()
    msgRect.topleft = (pos[0], pos[1])
    surface.blit(msgSurface, msgRect)


def CenterText(surface, pos, text, size=12, name='sans',
               color=(0, 0, 0),
               bold=False,
               italic=False,
               antialias=True):
    dim = MeasureText(text, name, size, bold, italic)
    DrawText(surface, (pos[0] - dim[0] / 2,
                       pos[1] - dim[1] / 2),
             text, size, name, color, bold, italic, antialias)


class LayoutParams:
    MATCH_PARENT = -1
    WRAP_CONTENT = -2

    def __init__(self):
        self.Index = None

    def Index(self, index):
        self.Index = index

    def MatchParent(self):
        return self

    def WrapContent(self):
        return self

    def Position(self, x, y):
        return self

    def Size(self, w, h):
        return self


class View:
    def __init__(self, context:AppContext):
        self.Context:AppContext = context
        self.Parent:View = None
        self.Rect:pygame.Rect = pygame.Rect(0, 0, 0, 0)
        self.BackgroundColor = (192, 192, 192)
        self.Movable = False
        self.Focus = False
        self.Focusable = False
        self.ClickAction = OnClickDoNothing
        self.LayoutParams = [MATCH_PARENT, MATCH_PARENT]
        self.MeasuredDimension:Dimension = Dimension()
        self.Visible = True
        self.MinDimension: Dimension = None
        self.Margin = 0
        self.BorderWidthTop = 0
        self.BorderWidthBottom = 0
        self.BorderWidthLeft = 0
        self.BorderWidthRight = 0
        self.BorderWidthColor = (0, 0, 0)
        self.Padding = 0
        self.Active = True

    def _load_image(self, name):
        return pygame.image.load(join(self.GraphicsPath, name))

    def _widget_to_window(self, point: Point) -> Point:
        """ Translate point which is relative to upper left corner of widget
            to a point relative to the upper left corner of the window """
        return Point(self.Rect.x, self.Rect.y) + point * (self.TileSize + 1)

    def SetActive(self, state):
        self.Active = state

    def SetMargin(self, margin):
        self.Margin = margin
        
    def SetBorderWidth(self, *args):
        if len(args) == 1:            
            self.BorderWidthTop = args[0]
            self.BorderWidthLeft = args[0]
            self.BorderWidthBottom = args[0]
            self.BorderWidthRight = args[0]
        elif len(args) == 2:
            self.BorderWidthTop = args[0]
            self.BorderWidthLeft = args[1]
            self.BorderWidthBottom = args[0]
            self.BorderWidthRight = args[1]           
        elif len(args) == 4:
            self.BorderWidthTop = args[0]
            self.BorderWidthLeft = args[1]
            self.BorderWidthBottom = args[2]
            self.BorderWidthRight = args[3]
        
    def SetPadding(self, padding):
        self.Padding = padding
        
    def SetParent(self, parent:View):
        self.Parent = parent

    def GetParent(self) -> View:
        return self.Parent

    def GetWidth(self):
        return self.Rect.width

    def GetHeight(self):
        return self.Rect.height
    
    def SetMinDimension(self, width, height):
        if width and height:
            self.MinDimension = Dimension(width, height)
        else:
            self.MinDimension = None

    def SetPosition(self, *args):
        if len(args) == 1 and isinstance(args[0], Point):
            self.Rect.x = args[0].X
            self.Rect.y = args[0].Y
        else:
            point = Point(*args)
            self.Rect.x = point.X
            self.Rect.y = point.Y

    def SetSize(self, width, height):
        self.Rect.size = (width, height)

    def GetPosition(self) -> Point:
        return Point(self.Rect.x, self.Rect.y)

    def SetBackgroundColor(self, color):
        self.BackgroundColor = color

    def IsPointInside(self, *args):
        point = Point(*args)
        return self.Rect.collidepoint(point.X, point.Y)

    def Intersection(self, other) -> pygame.Rect:
        return self.Rect.clip(other.Rect)

    def SetMeasuredDimension(self, width, height):
        self.MeasuredDimension.set(width, height)
        
    def GetMeasuredDimension(self):
        return self.MeasuredDimension

    # Do not override
    def _apply_min_dimension_measure(self):
        if self.MinDimension:
            self.MeasuredDimension.at_least(self.MinDimension)

    # Do not override. Override OnMeasure of specific View subclass instead.
    def Measure(self, widthMeasureSpec, heightMeasureSpec):
        self.OnMeasure(widthMeasureSpec, heightMeasureSpec)
        self.MeasuredDimension.widen(self.Padding * 2)
        self.MeasuredDimension.heigten(self.Padding * 2)
        self._apply_min_dimension_measure()
                    
    # Do not override. Override OnLayout of specific View subclass instead.
    def Layout(self, left, top, width, height):
        self.OnLayout(True, left, top, width, height)

    # Do not override. Override OnDraw of specific View subclass instead.
    def Draw(self, surface):
        if self.Visible:
            #pygame.draw.rect(surface, self.BackgroundColor, self.Rect, 0)
            
            self.OnDraw(surface)
            #if self.BorderWidthTop:
                
            #pygame.draw.rect(surface, (255, 0, 0), self.Rect, 1)
            #msgRect = pygame.Rect(self.Rect)
            #DrawText(surface, msgRect, self.__class__.__name__,
            #         size=16, color=(255, 255, 255))

    def OnMeasure(self, widthSpec, heightSpec):
        # Override in subclass!
        pass            

    def OnDraw(self, surface):
        # Override in subclass!
        pass

    def OnLayout(self, changed, left, top, width, height):
        # Override in subclass!
        self.Rect.left = left
        self.Rect.top = top
        self.Rect.width = width
        self.Rect.height = height
        pass

    def OnEvent(self, event):
        pass

    def OnClick(self, x, y):
        pass

    def OnMouseMove(self, x, y):
        pass

    def FindView(self, x, y):
        return self

class ViewGroup(View):
    def __init__(self, context):
        super().__init__(context)
        self.Children:list[View] = []

    def __len__(self):
        return len(self.Children)

    def AddChild(self, child:View) -> View:
        child.SetParent(self)
        self.Children.append(child)
        return child

    def GetChild(self, index) -> View:
        if index >= 0 and index < len(self.Children):
            return self.Children[index]
        return None

    def Clear(self):
        self.Children = []

    def FindView(self, x, y) -> View:
        for child in reversed(self.Children):
            if child.IsPointInside(x, y):
                return child.FindView(x, y)
        return None

    def BringToFront(self, view):
        try:
            i = self.Children.index(view)
            x = self.Children.pop(i)
            self.Children.append(x)
        except (ValueError, IndexError):
            return

    # Do not override
    def Measure(self, widthMeasureSpec, heightMeasureSpec):
        for child in self.Children:
            child.Measure(widthMeasureSpec, heightMeasureSpec)
        self.OnMeasure(widthMeasureSpec, heightMeasureSpec)
        self._apply_min_dimension_measure()

    # Do not override
    def Layout(self, left, top, width, height):
        for child in self.Children:
            child.Layout(left, top, width, height)
        self.OnLayout(True, left, top, width, height)

    # Do not override
    def Draw(self, surface):
        for child in self.Children:
            child.Draw(surface)

    
class LinearLayout(ViewGroup):
    HORIZONTAL = 1
    VERTICAL = 2
    def __init__(self, context, orientation=VERTICAL):
        super().__init__(context)
        self.Orientation = orientation
        #if self.Parent:
        #    self.SetPosition(self.Parent.GetPosition())
        #else:
        #    self.SetPosition((0, 0))

    def SetOrientation(self, orientation):
        self.Orientation = orientation

    def OnMeasure(self, widthMeasureSpec, heightMeasureSpec):
        """
        w = MeasureSpec(MeasureSpec.AT_MOST,
                        widthMeasureSpec.GetSize() / len(self.Children))
        """
        #for child in self.Children:
        #    child.OnMeasure(None, None)
            
        width = 0
        height = 0
        if self.Orientation == LinearLayout.HORIZONTAL:
            for child in self.Children:
                dim = child.GetMeasuredDimension()
                width += dim.width
                if dim.height > height:
                    height = dim.height
        elif self.Orientation == LinearLayout.VERTICAL:
            for child in self.Children:
                dim = child.GetMeasuredDimension()
                height += dim.height
                if dim.width > width:
                    width = dim.width
        self.SetMeasuredDimension(width, height)

    def OnLayout(self, changed, left, top, width, height):
        self.Rect.topleft = (left, top)
        self.Rect.size = (self.MeasuredDimension.width, self.MeasuredDimension.height)
        for child in self.Children:
            if self.Orientation == LinearLayout.HORIZONTAL:                
                w = child.GetMeasuredDimension().width
                child.OnLayout(changed, left, top, w, height)
                left += w
            if self.Orientation == LinearLayout.VERTICAL:                
                h = child.GetMeasuredDimension().height
                child.OnLayout(changed, left, top, width, h)
                top += h


class GridLayout(ViewGroup):
    def __init__(self, context, rows, columns):
        super().__init__(context)
        self.Rows = rows
        self.Columns = columns

    def OnMeasure(self, withMeasureSpec, heightMeasureSpec):
        self._max_row_heights = [0] * self.Rows
        self._max_col_widths = [0] * self.Columns
        for i, child in enumerate(self.Children):            
            col = i % self.Columns
            row = i // self.Columns
            dim = child.GetMeasuredDimension()
            if dim.width > self._max_col_widths[col]:
                self._max_col_widths[col] = dim.width
            if dim.height > self._max_row_heights[row]:
                self._max_row_heights[row] = dim.height
        width = sum(self._max_col_widths)
        height = sum(self._max_row_heights)
        self.SetMeasuredDimension(width, height)

    def OnLayout(self, changed, left, top, width, height):
        self.Rect.topleft = (left, top)
        self.Rect.size = (self.MeasuredDimension.width,
                          self.MeasuredDimension.height)

        for i, child in enumerate(self.Children):
            row = i // self.Columns
            col = i % self.Columns
            x = left + sum(self._max_col_widths[:col])
            y = top + sum(self._max_row_heights[:row])
            child.OnLayout(changed, x, y,
                           self._max_col_widths[col],
                           self._max_row_heights[row])

    def __repr__(self):
        return f'<GridLayout cols={self.Columns} rows={self.Rows}>'


class AbsoluteLayout(ViewGroup):
    def __init__(self, context: AppContext):
        super().__init__(context)
        self.Context = context

    def OnMeasure(self, widthMeasureSpec, heightMeasureSpec):
        width = 0
        height = 0
        for child in self.Children:
            child.OnMeasure(widthMeasureSpec, heightMeasureSpec)
            pos = child.GetPosition()
            dim = child.GetMeasuredDimension()
            if pos.X + dim.width > width:
                width = pos.X + dim.width
            if pos.Y + dim.height > height:
                height = pos.Y + dim.height
        self.SetMeasuredDimension(width, height)

    def OnLayout(self, changed, left, top, width, height):
        for child in self.Children:
            child.OnLayout(changed, left, top, width, height)


class TextView(View):
    def __init__(self, context, text=''):
        super().__init__(context)
        self.Text = text
        self.TextSize = 16
        self.TextColor = (0, 0, 0)
        self.FontName = "sans"
        self.Bold = False
        self.Italic = False
        self.Gravity = 0

    def SetTextSize(self, size):
        self.TextSize = size

    def SetText(self, text):
        self.Text = text

    def OnMeasure(self, widthMeasureSpec, heightMeasureSpec):
        font = pygame.font.SysFont(self.FontName, self.TextSize,
                                   self.Bold, self.Italic)
        width, height = font.size(self.Text)
        self.SetMeasuredDimension(width, height)

    def SetGravity(self, gravity):
        self.Gravity = gravity

    def OnDraw(self, surface):
        font = pygame.font.SysFont(self.FontName, self.TextSize,
                                   self.Bold, self.Italic)
        msgSurface = font.render(self.Text, True, self.TextColor)
        msgRect = msgSurface.get_rect()
        if self.Gravity == 0:
            msgRect.topleft = self.Rect.topleft
        if self.Gravity & CENTER_HORIZONTAL:
            msgRect.left = self.Rect.left + self.Rect.width / 2 - msgRect.width / 2
        surface.blit(msgSurface, msgRect)


class TextInputView(TextView):
    def __init__(self, context):
        super().__init__(context)
        self.Cursor = len(self.Text)
        self.Insert = True
        self.Password = False
        self.Focusable = True
        self.SetMinDimension(100, 10)

    def OnDraw(self, surface):
        pygame.draw.rect(surface, (255, 255, 255), self.Rect, 0)
        if self.Password:
            text = '*' * len(self.Text)
        else:
            text = self.Text

        DrawText(surface, self.Rect.topleft, text=text,
                 size=self.TextSize,
                 color=self.TextColor)

        if self.Focus:
            if self.Insert:
                DrawText(surface, self.Rect.topleft, text[0:self.Cursor] + '|',
                         size=self.TextSize,
                         color=self.TextColor)
            else:
                if self.Cursor > 0:
                    c = text[0:self.Cursor] + '_'
                else:
                    c = '_'
                self.DrawText(surface, self.Rect.topleft, c, self.TextSize,
                              color=self.TextColor)

    def SetText(self, text):
        self.Text = text
        self.Cursor = len(text)

    def OnEvent(self, event):
        if event.type == pygame.KEYDOWN:
            key = event.key
            if key == pygame.K_BACKSPACE:
                if len(self.Text) > 0:
                    self.Text = self.Text[0:len(self.Text) - 1]
                    self.Cursor -= 1
            elif key == pygame.K_INSERT:
                self.Insert = not self.Insert
            elif key == pygame.K_LEFT:
                if self.Cursor > 0:
                    self.Cursor -= 1
            elif key == pygame.K_RIGHT:
                if self.Cursor < len(self.Text):
                    self.Cursor += 1
            elif key == pygame.K_HOME:
                self.Cursor = 0
            elif key == pygame.K_END:
                self.Cursor = len(self.Text)
            elif key == pygame.K_DELETE:
                if self.Cursor == 0:
                    self.Text = self.Text[1:]
                else:
                    self.Text = self.Text[0:self.Cursor] + \
                        self.Text[self.Cursor + 1:]
            elif chr(key).isalnum():
                if self.Insert:
                    if self.Cursor == 0:
                        self.Text = chr(key) + self.Text
                    else:
                        self.Text = self.Text[0:self.Cursor] + \
                            chr(key) + self.Text[self.Cursor:]
                    self.Cursor += 1
                else:
                    if self.Cursor == 0:
                        self.Text = chr(key) + self.Text[1:]
                    else:
                        self.Text = self.Text[0:self.Cursor] + \
                            chr(key) + self.Text[self.Cursor + 1:]
                    self.Cursor += 1


class ButtonView(TextView):
    def __init__(self, context, text=''):
        super().__init__(context, text)
        self.Pressed = False
        self.Focusable = True
        self.Padding = 12

    def SetPressed(self, isPressed):
        self.Pressed = isPressed

    def IsPressed(self):
        return self.Pressed

    def OnEvent(self, event):
        if event.type == pygame.MOUSEBUTTONUP:
            self.Pressed = False
        if not self.Active:
            return
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.Pressed = True

    #def OnMeasure(self, widthMeasureSpec, heightMeasureSpec):
    #    self.SetMeasuredDimension(self._width, self._height)

    def OnDraw(self, surface):
        pressed = (250, 250, 128)
        normal = (72, 72, 72)
        inactive = (144, 144, 144)
        
        if self.IsPressed():
            pygame.draw.rect(surface, pressed, self.Rect, 0)
            color = normal
        else:
            pygame.draw.rect(surface, normal, self.Rect, 0)
            color = pressed

        if not self.Active:
            color = inactive
            
        CenterText(surface, (self.Rect.left + self.Rect.width / 2,
                             self.Rect.top + self.Rect.height / 2),
                   text=self.Text,
                   size=self.TextSize,
                   bold=True,
                   color=color)


class ImageView(View):
    def __init__(self, context, filename=None):
        super().__init__(context)
        self.Image = None
        if filename:
            self.LoadImage(filename)

    def LoadImage(self, filename):
        if filename.rsplit('.', 1)[-1].lower() == 'png':
            self.Image = self._load_image(filename)

    def OnMeasure(self, width, height):
        if self.Image:
            self.SetMeasuredDimension(self.Image.get_width(),
                                      self.Image.get_height())
        
    def OnDraw(self, surface):
        surface.blit(self.Image, self.Rect)


class CheckboxView(View):
    def __init__(self, context, checked:bool=False):
        super().__init__(context)
        self.Checked = checked
        self.ClickAction = self.OnClick

    def OnMeasure(self, width, height):
        self.SetMeasuredDimension(20, 20)

    def OnClick(self, pos:Point, view:View, button:int):
        print(f'OnClick({pos}, {view})')
        self.Checked = not self.Checked

    def OnDraw(self, surface):
        inside = self.Rect.inflate(-2, -2)
        pygame.draw.rect(surface, ALMOST_WHITE, inside)
        pygame.draw.rect(surface, ALMOST_BLACK, self.Rect, 1)
        if self.Checked:
            cross = inside.inflate(-2, -2)
            pygame.draw.line(
                surface, ALMOST_BLACK, cross.topleft, cross.bottomright, 2
            )
            pygame.draw.line(
                surface, ALMOST_BLACK, cross.topright, cross.bottomleft, 2
            )


class DragInfo:
    def __init__(self):
        self.Offset:Point = None
        self.View:View = None
        self.SaveX = 0
        self.SaveY = 0
        self.Dragging = False

    def BeginDrag(self, pos, view):
        self.Offset = Point.FromTuple(pos) - \
            Point.FromTuple(view.GetPosition())
        self.View = view
        if view is not None:
            (self.SaveX, self.SaveY) = view.GetPosition()
        self.Dragging = True

    def Update(self, pos):
        if self.View is not None:
            self.View.SetPosition(Point(pos) - self.Offset)

    def GetSavedViewPos(self):
        return (self.SaveX, self.SaveY)

    def EndDrag(self):
        self.View = None
        self.Dragging = False

    def IsDragging(self):
        return self.Dragging

    def RestoreView(self):
        self.View.SetPosition((self.SaveX, self.SaveY))


class AppContext:
    DESIRED_FPS = 30
    
    def __init__(self, width, height):
        self.Callback = None

        self.ActivityStack = []
        self.Activities = {}

        self.CurrentActivity = None

        self.ContentView = None

        pygame.init()
        self.Surface = pygame.display.set_mode((width, height),
                                               pygame.DOUBLEBUF, 32)
        
        self._desired_fps = AppContext.DESIRED_FPS
        self._running = True
        self._render_time = 0

    @property
    def desired_fps(self):
        return self._desired_fps
    
    async def on_startup(self):
        pass
    
    async def on_shutdown(self):
        pass
    
    async def pygame_task(self):
        await self.on_startup()

        t0 = monotonic()
        while self.IsRunning():
            if pygame.event.peek():
                self.CurrentActivity.DefaultEventHandler()
            t1 = monotonic()
            dt = t1 - t0
            t0 = t1
            self.OnLoop(dt)
            r0 = monotonic()
            self.CurrentActivity.Render()
            self._render_time = monotonic() - r0
            pygame.display.flip()
            await asyncio.sleep(1 / self.desired_fps)
        logging.debug('Exiting pygame_task')
        
        await self.on_shutdown()

    def RenderTime(self):
        return self._render_time

    def RegisterActivity(self, activity):
        name = activity.GetName()
        if name in self.Activities:
            logging.error(f"There is already an acticity called {name}")
            raise RuntimeError(f'Activity "{name}" already registered')
        self.Activities[name] = activity
        return activity

    def StartActivity(self, activityName):
        if activityName in iter(self.Activities.keys()):
            if self.CurrentActivity:
                self.CurrentActivity.Deactivate()
            self.CurrentActivity = self.Activities[activityName]
            self.ActivityStack.append(self.CurrentActivity)
            self.CurrentActivity.Activate()
            logging.debug(f'Activated {activityName}')
        else:
            logging.error(f'Can\'t find activity {activityName}')

    def ExitActivity(self):
        logging.debug('ExitActivity')
        self.CurrentActivity.Deactivate()
        self.ActivityStack.pop()
        if len(self.ActivityStack) == 0:
            self.RequestStop()
        else:
            self.CurrentActivity = self.ActivityStack[-1]
            self.CurrentActivity.Activate()
            
    def RequestStop(self):
        """ Do not override """
        logging.info('RequestStop')
        self._running = False
        self.OnStopRequested()
        
    def IsRunning(self):
        return self._running

    def OnLoop(self, dt):
        """ Override """
        pass

    def OnStopRequested(self):
        """ Override """
        pass


class Activity:
    def __init__(self, context, name):
        self.Context:AppContext = context
        self.Name = name
        self.ContentView = None
        self.BackgroundColor = (66, 66, 66)

        self.MousePos = (0, 0)
        self.FocusView = None
        self.HoverView = None
        self.MouseDownPos = None
        self.MouseDownView = None
        self.MouseUpView = None
        self.Initialized = False
        self.DragInfo = DragInfo()

    def GetName(self):
        return self.Name

    def OnInit(self):
        pass


    # Is called for each event. Can be overridden by subclass.
    # If False is returned, the default event handler is run.
    # If True is returned, the default event handler is not run.
    def HandleEvent(self, event):
        return False

    def DefaultEventHandler(self):
        for event in pygame.event.get():
            if self.HandleEvent(event):
                continue

            if event.type == pygame.QUIT:
                self.Exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.Exit()

            elif event.type == pygame.MOUSEMOTION:
                self.HoverView  = self.ContentView.FindView(event.pos[0],
                                                            event.pos[1])

                if self.MouseDownPos is not None and not self.DragInfo.IsDragging():
                    if self.MouseDownView is not None and self.MouseDownView.Movable:
                        self.DragInfo.BeginDrag(event.pos, self.MouseDownView)
                        self.OnDragBegin(event.pos, self.MouseDownView)

                if self.DragInfo.View:
                    self.DragInfo.Update(event.pos)

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.MouseDownPos = event.pos
                self.MouseDownView = self.ContentView.FindView(event.pos[0],
                                                               event.pos[1])

                self.MouseUpView = None

                fw = self.FocusView
                self.FocusView = self.MouseDownView
                if fw != self.FocusView:
                    if fw is not None:
                        fw.Focus = False
                    if self.FocusView is not None:
                        self.FocusView.Focus = True

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.MouseUpView = self.ContentView.FindView(event.pos[0],
                                                             event.pos[1])
                if self.MouseUpView == self.MouseDownView:
                    if self.MouseDownView and not self.DragInfo.IsDragging():
                        if self.MouseDownView.Active:
                            self.MouseDownView.ClickAction(event.pos,
                                                           self.MouseDownView, 
                                                           event.button)

                if self.DragInfo.IsDragging():
                    self.OnDragEnd(event.pos, self.MouseDownView, self.DragInfo.GetSavedViewPos())
                    self.DragInfo.EndDrag()

                self.MouseDownView = None
                self.MouseDownPos = None
                self.MouseUpView = None

            if self.FocusView:
                self.FocusView.OnEvent(event)


    def Exit(self):
        self.Context.ExitActivity()

    def SetContentView(self, view):
        self.ContentView = view

    def Render(self):
        if self.ContentView:
            width = self.Context.Surface.get_width()
            height = self.Context.Surface.get_height()
            self.Context.Surface.fill(GRAY_50)
            self.ContentView.Measure(None, None)
            self.ContentView.Layout(0, 0, width, height)
            self.ContentView.Draw(self.Context.Surface)

    def StartActivity(self, activityName):
        self.Context.Callback.StartActivity(activityName)

    # Do not override
    def Activate(self):
        logging.debug(f'Activate "{self.Name}"')
#        self.PushEventHandler(self.DefaultEventHandler)
        if not self.Initialized:
            self.OnInit()
            if self.ContentView is None:
                logging.error("OnInit must set a content view")
                return
            self.Initialized = True
        self.OnActivate()

    # Do not override
    def Deactivate(self):
        logging.debug(f'Deactivate "{self.Name}"')
        self.OnDeactivate()
#        self.PopEventHandler()

    def OnActivate(self):
        pass

    def OnDeactivate(self):
        pass

    def OnDragBegin(self, pos, view):
        pass

    def OnDragEnd(self, pos, view, savedViewPos):
        pass
