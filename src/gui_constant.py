APP_TITLE: str = "SnapSum4J"

WINDOW_WIDTH: int = 600
WINDOW_HEIGHT: int = 1100

HEAD: str = "数字识别与求和工具"

MAIN_FROM_PADX: int = 20
MAIN_FROM_PADY: int = 20

HEADER_FONT: tuple[str, int, str] = ("微软雅黑", 16, "bold")

TITLE_LABEL_PADY: int = 10

UPLOAD_FRAME_PADY: int = 10
UPLOAD_BUTTON_TEXT: str = "选择图片"
UPLOAD_BUTTON_PADX: int = 5
CAPTURE_BUTTON_TEXT: str = "截取屏幕区域"
CAPTURE_BUTTON_PADX: int = 5

DIGITS_PADY: int = 10
DIGITS_DESC: str = "识别到的数字（每行一个，可手动添加）:"
DIGITS_DESC_PADY: int = 5
DIGITS_TEXT_HEIGHT: int = 10
DIGITS_TEXT_WIDTH: int = 60
DIGITS_TEXT_FONT: tuple[str, int] = ("Courier New", 12)
DIGITS_TEXT_PADX: int = 5

SUM_PADY: int = 10
SUM_LABEL_TEXT: str = "总和:"
SUM_LABEL_FONT: tuple[str, int, str] = ("微软雅黑", 10, "bold")
SUM_LABEL_PADX: int = 5
SUM_LABEL_PADY: int = 5
SUM_RESULT_WIDTH: int = 20
SUM_RESULT_FONT: tuple[str, int] = ("Courier New", 12)
SUM_RESULT_ENTRY_PADX: int = 5

TOPMOST_TEXT: str = "窗口置顶"
TOPMOST_PADY: int = 5

STATUS_LABEL_FONT: tuple[str, int] = ("微软雅黑", 9)
STATUS_LABEL_PADY: int = 5

CHOSEN_IMAGE_DESC: str = "已选择图片:"

PREVIEW_WINDOW_TITLE: str = "图片预览 - 请框选要识别的区域"
PREVIEW_WINDOW_RELAX_HEIGHT: int = 100

PREVIEW_OUTLINE_COLOR: str = "red"
PREVIEW_OUTLINE_WIDTH: int = 2
PREVIEW_WARNING_TITLE: str = "提示"
PREVIEW_WARNING_MESSAGE: str = "请选择一个更大的区域"
PREVIEW_CONFIRM_WARNING_TITLE: str = "提示"
PREVIEW_CONFIRM_WARNING_MESSAGE: str = "请先选择一个区域"
PREVIEW_BUTTON_FRAME_PADY: int = 20
PREVIEW_CONFIRM_BUTTON_TEXT: str = "确认选择"
PREVIEW_CONFIRM_BUTTON_FONT: tuple[str, int] = ("微软雅黑", 12)
PREVIEW_CONFIRM_BUTTON_WIDTH: int = 15
PREVIEW_CONFIRM_BUTTON_PADY: int = 10
PREVIEW_HINT_TEXT: str = "提示: 按住鼠标左键拖拽选择要识别的区域，可反复选择直到点击确认"
PREVIEW_HINT_PADY: int = 10
PREVIEW_ERROR_TITLE: str = "错误"
PREVIEW_ERROR_MESSAGE: str = "无法加载图片: "

TOPMOST_ENABLE_MESSAGE: str = "窗口已置顶"
TOPMOST_DISABLE_MESSAGE: str = "窗口已取消置顶"

SCREEN_CAPTURE_WARNING_TITLE: str = "提示"
SCREEN_CAPTURE_WARNING_MESSAGE: str = "请选择一个更大的区域"
SCREEN_CAPTURE_CANCEL_DELAY: int = 100
