from django.shortcuts import render


def AboutAuthorView(request):
    title = 'Об авторе'
    template_path = 'about/author.html'
    content = {'title': title}
    return render(request, template_path, content)


def AboutTechView(request):
    title = 'Технологии'
    template_path = 'about/tech.html'
    content = {'title': title}
    return render(request, template_path, content)
