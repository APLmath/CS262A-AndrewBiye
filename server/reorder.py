def reorder(data, max_points=4):
  def reorder_helper(data, minX, maxX, minY, maxY):
    if len(data) <= max_points:
      return [id for id, x, y in data]
    midX = (minX + maxX) / 2
    midY = (minY + maxY) / 2
    buckets = [[], [], [], []]
    for id, x, y in data:
      buckets[(2 if y > midY else 0) + (1 if x > midX else 0)].append((id, x, y))
    reorderings = [
      reorder_helper(buckets[0], minX, midX, minY, midY),
      reorder_helper(buckets[1], midX, maxX, minY, midY),
      reorder_helper(buckets[2], minX, midX, midY, maxY),
      reorder_helper(buckets[3], midX, maxX, midY, maxY)
    ]
    final_reordering = []
    i = 0
    while reorderings:
      i %= len(reorderings)
      if len(reorderings[i]):
        final_reordering.append(reorderings[i].pop(0))
        i += 1
      else:
        reorderings.pop(i)
    return final_reordering

  minX = data[0][1]
  maxX = minX
  minY = data[0][2]
  maxY = minY
  for id, x, y in data[1:]:
    minX = min(x, minX)
    maxX = max(x, maxX)
    minY = min(y, minY)
    maxY = max(y, maxY)
  minX = float(minX)
  maxX = float(maxX)
  minY = float(minY)
  maxY = float(maxY)

  return reorder_helper(data, minX, maxX, minY, maxY)
