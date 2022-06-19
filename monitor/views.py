import json
from django.shortcuts import render
from django.http import JsonResponse
from hubinfo.models import SPDsLinks, EPsLinks


# nodes_idx_to_name = {
#     1: 'ece-1',
#     2: 'ece-2',
#     3: 'mse-1',
#     4: 'pas-1',
#     5: 'pas-2',
#     6: 'osc-1',
#     7: 'osc-2',
#     8: 'osc-3',
#     9: 'osc-4',
#     10: 'osc-5',
#     11: 'bio-1',
#     12: 'bio-2',
#     13: 'bio-3',
#     14: '',
#     15: '',
#     16: ''
# }  # total: 13
#

def maps(request):
    """
    Real-time network status visualization
    An example
    """
    with open('config.json', 'r') as f:
        gmap_api_key = json.load(f)['GMAP_API_KEY']
    return render(request, 'admin/monitor/maps.html', {'gmap_api_key': gmap_api_key})


def maps_status(request):
    """
    Query database, return active nodes occupying EPs channels and SPDs channels, respectively
    Return result by AJAX
    """

    eps_links = EPsLinks.objects.filter(linkage=True, in_use=True)  # user number <= 5
    spds_links = SPDsLinks.objects.filter(linkage=True, in_use=True)  # user number <= 8

    eps_act_nodes = []
    spds_act_nodes = []
    for link in eps_links:
        node = str(link.lab.lab_name)
        if node not in eps_act_nodes and not node.startswith('res'):
            eps_act_nodes.append(node)
    for link in spds_links:
        node = str(link.lab.lab_name)
        if node not in spds_act_nodes and not node.startswith('res'):
            spds_act_nodes.append(node)

    res = {
        'EPsActNodes': eps_act_nodes,
        'SPDsActNodes': spds_act_nodes
    }
    return JsonResponse(res)
