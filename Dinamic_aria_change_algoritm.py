import networkx as nx
from collections import deque

# алгоритм Брандеса с указанием списка вершин по которым ходить 
def brandes_partial(G, affected_nodes):
    
    
    
    
    C_B = {v: 0 for v in affected_nodes}
    
    for s in affected_nodes:
        S = []
        P = {w: [] for w in affected_nodes}
        sigma = {t: 0 for t in affected_nodes}
        sigma[s] = 1
        d = {t: -1 for t in affected_nodes}
        d[s] = 0
        Q = deque()
        Q.append(s)

        while Q:
            v = Q.popleft()
            S.append(v)
            for w in G.neighbors(v):
                if w not in affected_nodes:
                    continue
                if d[w] < 0:
                    Q.append(w)
                    d[w] = d[v] + 1
                if d[w] == d[v] + 1:
                    sigma[w] = sigma[w] + sigma[v]
                    P[w].append(v)

        delta = {v: 0 for v in affected_nodes}
        while S:
            w = S.pop()
            for v in P[w]:
                delta[v] = delta[v] + (sigma[v] / sigma[w]) * (1 + delta[w])
            if w != s:
                C_B[w] += delta[w]

    # Делим все центральности на 2
    for v in C_B:
        C_B[v] /= 2

    return C_B
# функция пересчитывает C_B для добавленный вершин и 2 поколений их соседей
def add_node_and_update(G, new_node, new_edges):
    # Добавляю врершины и ребра в граф 
    G.add_node(new_node)
    for u, v in new_edges:
        G.add_edge(u, v)
    
    # задейственные узлы - подграф для пересчета 
    affected_nodes = set()
    
    # добавляю сами добавленные 
    for u, v in new_edges:
        affected_nodes.add(u)
        affected_nodes.add(v)
    
    # Добавляю соседей в пределах 2 шагов в набор задейственных
    for node in list(affected_nodes):
        affected_nodes.update(G.neighbors(node))
        for neighbor in G.neighbors(node):
            affected_nodes.update(G.neighbors(neighbor))

    # Пересчитаю степень для выбранных вершин 
    C_B_partial = brandes_partial(G, affected_nodes)
    
    return C_B_partial

# пересчет при удаление вершин
def remove_node_and_update(G, node_to_remove):
    affected_nodes = set(G.neighbors(node_to_remove))
    
    for node in list(affected_nodes):
        affected_nodes.update(G.neighbors(node))
        for neighbor in G.neighbors(node):
            affected_nodes.update(G.neighbors(neighbor))

    G.remove_node(node_to_remove)

    C_B_partial = brandes_partial(G, affected_nodes)
    
    return C_B_partial

# функция процентного откланения по каждой вершине 
def calculate_percentage_deviation(C_B1, C_B2):
   
    deviations = {}
    for node in C_B1:
        if node in C_B2:
            original = C_B1[node]
            updated = C_B2[node]
            if original != 0:
                deviation = ((updated - original) / original) * 100
            else:
                deviation = 0.0 if updated == 0 else float('inf')
            deviations[node] = deviation
        else:
            deviations[node] = float('inf')
    
    return deviations

# функция считает среднее отклонение 
def percentage_deviation(array1, array2):
   
    if len(array1) != len(array2):
        raise ValueError("Both arrays must have the same length")
    
    total_deviation = 0.0
    n = len(array1)
    
    for i in range(n):
        if array1[i] != 0:  # To avoid division by zero
            deviation = abs(array1[i] - array2[i]) / array1[i] * 100
        else:
            deviation = abs(array1[i] - array2[i]) * 100  # If both are zero, deviation is zero
        total_deviation += deviation

    average_deviation = total_deviation / n
    return average_deviation


# Пример использования
# обноваляю только соседние 2 поколения 
# G = nx.erdos_renyi_graph(599, 0.03, seed=42)
G = nx.Graph()

G.add_node(1)
G.add_node(2)
G.add_node(3)
G.add_node(4)
G.add_node(5)

G.add_edge(1,2)
G.add_edge(1,4)
G.add_edge(2,3)
G.add_edge(2,5)
G.add_edge(3,5)
G.add_edge(4,5)





print(G.number_of_edges())
# G = nx.karate_club_graph()
new_node = 5
new_edges = []
C_B_updated = add_node_and_update(G, new_node, new_edges)

# точно посчитатанный граф с добавленными вершинами 
G1 = G.copy()
# G1.add_node(600)
# G1.add_edge(600,0)
# G1.add_edge(600,597)





C_B_initial = brandes_partial(G1, G1.nodes())

print("Initial Betweenness Centrality:", C_B_initial)
print()

# замененяю пересчитанные вершины 
C_B_COPY = C_B_initial.copy()
# Обновляем значения центральности в C_B_initial значениями из C_B_updated
for node in C_B_updated:
    if node in C_B_COPY:
        C_B_COPY[node] = C_B_updated[node]

print("Update Betweenness Centrality:", C_B_COPY)
print()


deviations = calculate_percentage_deviation(C_B_initial, C_B_COPY)
print("Percentage Deviations:", deviations)
print()


# Преобразование словарей в списки значений, упорядоченных по ключам
C_B_initial_values = [C_B_initial[node] for node in sorted(C_B_initial)]
C_B_COPY_values = [C_B_COPY[node] for node in sorted(C_B_COPY)]

deviation = percentage_deviation(C_B_initial_values, C_B_COPY_values)
print(f"Percentage Deviation: {deviation:.2f}%")
