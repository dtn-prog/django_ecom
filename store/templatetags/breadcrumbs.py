from django import template
from django.urls import reverse, resolve
from django.urls.exceptions import Resolver404

register = template.Library()

@register.simple_tag(takes_context=True)
def generate_breadcrumbs(context):
    request = context.get("request")
    path = request.path.strip("/")
    parts = path.split("/")
    breadcrumbs = [{'name': 'Trang chủ', 'url': reverse('store:home')}]
    url = ''
   
    for i, part in enumerate(parts):
        url += f'/{part}'
        #print(f"Trying to resolve: {url}")  # Debug print
        try:
            resolved = resolve(url)
        except Resolver404:
            try:
                resolved = resolve(url + '/')  # Try with trailing slash
                url += '/'
            except Resolver404:
                #print(f'Could not resolve URL: {url}')
                continue
        
        #print(f"Resolved: {resolved}")  # Debug print
        if resolved.namespace:
            url_name = f'{resolved.namespace}:{resolved.url_name}'
        else:
            url_name = resolved.url_name
        path_name = resolved.url_name.replace('_', ' ')
        crumb_name = context.get('title', path_name).title()
        full_url = reverse(url_name, args=resolved.args, kwargs=resolved.kwargs)
        #print(f"Reversed URL: {full_url}")  # Debug print
        breadcrumbs.append({'name': crumb_name, 'url': full_url})
   
    return breadcrumbs