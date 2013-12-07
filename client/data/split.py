import random
def output(lines,order,file="data",limit=100000,header=False,head=""):
    n=len(order)
    id=0
    for i in range(n):
        if (i%limit==0):
            if i>0:
                out.close()
            out=open(file+str(id)+".txt","w")
            if (header):
                out.write(head)
            id+=1
        out.write(lines[order[i]])
        i+=1
    out.close()

def getNeighbor(f,x,y,bw,W,H):
    sum=0
    for i in range(x-bw,x+bw+1):
        for j in range(y-bw,y+bw+1):
            if i>=0 and i<W and j>=0 and j<H:
                sum+=f[j][i]
    return sum

def reorder(data,resolution=(800,600),lat=[-90,90],lng=[-180,180],bw=2):
    n=len(data)
    id=range(n)
    random.shuffle(id)
    (W,H)=resolution
    f=[[0]*(W+2) for i in range(H+2)]
    weight=[[0,i] for i in range(n)]
    tot=0
    for i in id:
        tot+=1
        if tot%100000==0:
            print tot
        (y,x)=data[i]
        px=int((x-lng[0])/(lng[1]-lng[0])*W)
        py=int((y-lat[0])/(lat[1]-lat[0])*H)
        try:
            f[py][px]+=1
        except:
            print py,px
        weight[i][0]=getNeighbor(f,px,py,bw,W,H)+max(f[py][px]-4,0)*n
    weight.sort()
    print weight[:20]
    print [data[d[1]] for d in weight[:20]]
    return [w[1] for w in weight]

def parse(line,id=[1,2],sep=","):
    l=line.split(sep)
    try:
        return (float(l[id[0]]),float(l[id[1]]))
    except:
        print l

        
lines=open("earthquakes.csv").readlines()
data=map(parse,lines[1:])
id=reorder(data,bw=3)
output(lines,id,"earth",header=True,head=lines[0],limit=30000)


#lines=filter(lambda x:len(x)>1,open("dat.txt").readlines())
#data=map(lambda x:parse(x,[2,3],"\t"),lines)
#id=reorder(data,lat=[23,48],lng=[-126,-65],bw=4)
#output(lines,id,"data",limit=50000)
    

    
