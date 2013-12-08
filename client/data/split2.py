def output(lines,file="data",limit=100000,header=False,head=""):
    for i in range((len(lines) - 1) / limit + 1):
        filename = file + str(i) + ".txt"
        out = open(filename, "w")
        if header:
            out.write(head)
        for line in lines[i * limit: (i + 1) * limit]:
            out.write(line)
        out.close()
        print filename + ' written'

def reorder(lines, max_points=10):
    data = map(lambda line: (parse(line), line), lines)

    # First, find the global min and max
    (minY, minX), line = data[0]
    (maxY, maxX), line = data[0]
    for (y, x), line in data[1:]:
        minX = min(x, minX)
        minY = min(y, minY)
        maxX = max(x, maxX)
        maxY = max(y, maxY)

    def reorder_helper(data, minX, maxX, minY, maxY):
        if len(data) <= max_points:
            return map(lambda d: d[1], data)
        midX = (minX + maxX) / 2
        midY = (minY + maxY) / 2
        buckets = [[], [], [], []]
        for (y, x), line in data:
            buckets[(2 if y > midY else 0) + (1 if x > midX else 0)].append(((y, x), line))
        orders = [
            reorder_helper(buckets[0], minX, midX, minY, midY),
            reorder_helper(buckets[1], midX, maxX, minY, midY),
            reorder_helper(buckets[2], minX, midX, midY, maxY),
            reorder_helper(buckets[3], midX, maxX, midY, maxY),
        ]
        final_order = []
        i = 0
        while orders:
            i %= len(orders)
            if len(orders[i]):
                final_order.append(orders[i].pop(0))
                i += 1
            else:
                orders.pop(i)
        return final_order

    ret = reorder_helper(data, minX, maxX, minY, maxY)
    print 'Done!'
    return ret

def parse(line,id=[1,2],sep=","):
    l=line.split(sep)
    try:
        return (float(l[id[0]]),float(l[id[1]]))
    except:
        print l

        
lines=open("earthquakes.csv").readlines()
data=map(parse,lines[1:])
output(reorder(lines[1:]),"earth",header=True,head=lines[0],limit=30000)

