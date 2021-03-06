import math

def pointCloudToLines(pointCloud):
  lines = []
  line = []
  lastY = None

  for point in pointCloud:
    if lastY is not None and lastY != point.y:
      lines.append(line)
      line = []
    
    line.append(point)
    lastY = point.y

  lines.append(line)

  return lines

def linesToPointCloud(lines):
  return [point for line in lines for point in line]

def pointOnCircle(radius, angle):
  angleInRadians = math.radians(angle)

  x = radius * math.sin(angleInRadians)
  y = radius * math.cos(angleInRadians)

  return (x, y)
  