import collections
import heapq
import math

def astar(start: tuple, target: tuple, adjacent: "function", heuristic: "function") -> list:
    Node = collections.namedtuple("Node", ("heuristiccost", "cost", "coord", "previous"))

    ## Nodes to explore
    exploreheap = list()
    ## Nodes already explored
    cache = dict()

    ## Add start node to heap and cache
    heuristiccost = heuristic(start, target)
    startnode = Node(heuristiccost, 0,start,None)
    heapq.heappush(exploreheap, startnode)
    cache[start] = startnode

    ## On each iteration, remove lowest cost 
    while exploreheap and (currentnode := heapq.heappop(exploreheap)).coord != target:
        ## Cannot reach target
        if math.isinf(currentnode.heuristiccost): continue
        for (newcoord, movecost) in adjacent(currentnode.coord):
            costtonode = currentnode.cost + movecost
            if newcoord in cache:
                ## It is faster to go from currentnode to the new node
                ## than from the new node's previous node that was cached
                if costtonode < cache[newcoord].cost:
                    ## Update with this cost and previous node
                    cache[newcoord].cost = costtonode
                    cache[newcoord].previous = currentnode
                ## return (because this node was already explored/on the heap)
                continue

            ## Best guess at total cost to target via this node
            heuristiccost = costtonode + heuristic(newcoord, target)

            ## Add node to heap and cache
            newnode = Node(heuristiccost, costtonode, newcoord, currentnode)
            heapq.heappush(exploreheap, newnode)
            cache[newcoord] = newnode

    if currentnode.coord == target:
        route = [currentnode.coord]
        while (currentnode := currentnode.previous):
            route.append(currentnode.coord)
        return reversed(route)

    return None