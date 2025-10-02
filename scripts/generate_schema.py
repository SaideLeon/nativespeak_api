import os, sys, traceback, json
sys.path.append(r'C:\Users\Rogerio\Desktop\Modulos\NativeSpeak\nativespeak_api')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nativespeak_api.settings')

try:
    import django
    django.setup()
    from rest_framework.schemas.openapi import SchemaGenerator
    gen = SchemaGenerator(title='NativeSpeak API', version='1.0.0')
    schema = gen.get_schema(request=None, public=True)
    print(json.dumps(schema, indent=2, ensure_ascii=False)[:1000])
    print('\nSchema generated successfully')
except Exception:
    print('ERROR')
    traceback.print_exc()
