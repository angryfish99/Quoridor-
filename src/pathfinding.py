from collections import deque
import heapq

def heuristic(a, goals):
    # Manhattan distance to the closest goal
    # goals is a list of (r, c). For Quoridor, it's usually a whole row.
    # Closest goal in the row is just abs(r - goal_row)
    # Assumes set of goals share a row
    if not goals: return 0
    goal_row = goals[0][0] # All goals in Quoridor are on the same row (0 or 8)
    return abs(a[0] - goal_row)

def a_star(board, start, goals, return_path=False):
    """
    A* Search to find the shortest path from start to any of the goal states.
    Faster than BFS for single target direction.
    """
    # Priority Queue: (f_score, g_score, current_node)
    
    start_h = heuristic(start, goals)
    open_set = []
    heapq.heappush(open_set, (start_h, 0, start))
    
    g_score = {start: 0}
    came_from = {} # For path reconstruction
    
    goal_rows = {g[0] for g in goals}
    
    while open_set:
        f, g, current = heapq.heappop(open_set)
        
        if current[0] in goal_rows:
            if return_path:
                path = []
                curr = current
                while curr in came_from:
                    path.append(curr)
                    curr = came_from[curr]
                path.append(start)
                pass # path is reversed
                return g, path[::-1]
            return g
        
        if g > g_score.get(current, float('inf')):
            continue
        
        neighbors = board.get_valid_moves(*current, check_walls_only=True)
        
        for neighbor in neighbors:
            tentative_g = g + 1
            if tentative_g < g_score.get(neighbor, float('inf')):
                g_score[neighbor] = tentative_g
                came_from[neighbor] = current
                h = heuristic(neighbor, goals)
                heapq.heappush(open_set, (tentative_g + h, tentative_g, neighbor))
                
    if return_path:
        return float('inf'), []
    return float('inf')

# Alias for compatibility if needed, but we should switch usages
def bfs(board, start, goals):
    return a_star(board, start, goals)

def is_path_exists(board, start, goals):
    return a_star(board, start, goals) != float('inf')

def get_shortest_path(board, start, goals):
    _, path = a_star(board, start, goals, return_path=True)
    return path
