import os, sys, traceback
sys.path.append(r'C:\Users\Rogerio\Desktop\Modulos\NativeSpeak\nativespeak_api')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nativespeak_api.settings')

try:
    import django
    django.setup()
    from rest_framework.schemas import get_schema_view
    from django.test import RequestFactory
    from django.views.generic import TemplateView
    from django.urls import reverse

    rf = RequestFactory()

    # Schema view
    try:
        schema_view = get_schema_view(title='NativeSpeak API', description='API for NativeSpeak', version='1.0.0')
        req = rf.get('/api/schema/')
        resp = schema_view(req)
        print('Schema view response status:', getattr(resp, 'status_code', None))
        if getattr(resp, 'status_code', None) != 200:
            print('Schema response content:')
            try:
                content = resp.rendered_content
            except Exception:
                content = getattr(resp, 'content', None)
            print(content)
    except Exception:
        print('Exception generating schema:')
        traceback.print_exc()

    # Docs view (use the 'index.html' path that exists in the rest_framework package)
    try:
        docs_view = TemplateView.as_view(template_name='rest_framework/docs/index.html', extra_context={'schema_url': 'openapi-schema'})
        req = rf.get('/api/docs/')
        resp = docs_view(req)
        print('Docs view response status:', getattr(resp, 'status_code', None))
        try:
            content = resp.rendered_content
        except Exception:
            content = getattr(resp, 'content', None)
        print('Docs content length:', len(content) if content else None)
    except Exception:
        print('Exception rendering docs:')
        traceback.print_exc()

except Exception:
    print('Django setup error:')
    traceback.print_exc()
