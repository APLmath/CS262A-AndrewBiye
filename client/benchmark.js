/**
 * benchmark.js provides a simple harness to snapshot an SVG element over time.
 *
 * To use:
 * 1. Call benchmark.start with the SVG to watch.
 * 2. Call benchmark.snapshot to create a snapshot.
 * 3. Call benchmark.end when finished. This will return the list of snapshots.
 */

benchmark = (function() {
// The benchmark object.
var benchmark = {};
// The SVG node to observe.
var svg;
// Start time in milliseconds.
var startTime = 0;
// Snapshots.
var snapshots = [];

benchmark.start = function(svgToObserve) {
  svg = svgToObserve;
  snapshots = [];
  startTime = (new Date()).getTime();
  benchmark.snapshot();
};

benchmark.snapshot = function() {
  var startSnapshotTime = (new Date()).getTime();
  snapshots.push({
    'time': startSnapshotTime - startTime,
    'svg': svg.cloneNode(true);
  });
  startTime += (new Date()).getTime() - startSnapshotTime;
};

benchmark.end = function() {
  benchmark.snapshot();
  return snapshots;
};

return benchmark;
})();