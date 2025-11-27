import traceback
try:
    import contextily as ctx
    print('OK', getattr(ctx, '__version__', 'unknown'))
    print('providers present:', hasattr(ctx, 'providers'))
except Exception:
    traceback.print_exc()
