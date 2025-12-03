from django.shortcuts import render

def campaigns(request):
    return render(request, "campaigns/campaigns.html")

