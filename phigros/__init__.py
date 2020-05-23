from .chart import *

try:
    from .view import *
except ImportError:
    def preview(*args, **kwargs):
        import sys
        sys.exit('To use the preview feature, you have to install \"Cocos2D Python\". Aborted.\n'
                 'Cocos2D Python 未安装。无法启动预览。')
