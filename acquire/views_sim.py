"""
Data acquisition views functions.
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def index(request):
    return render(request, 'acquire.html')

# TODO
# 图形库，user-specific figure

# TODO
# 每一个新标签页生成一个token uuid
