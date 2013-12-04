/**
 * benchmark.js provides a simple harness to snapshot an canvas element over time.
 *
 * To use:
 * 1. Call benchmark.start with the canvas to watch.
 * 2. Call benchmark.snapshot to create a snapshot.
 * 3. Call benchmark.end when finished. This will return the list of snapshots.
 */

(function(exports) {
// The benchmark object.
var benchmark = {};
// The canvas node to observe.
var canvas;
// Start time in milliseconds.
var startTime = 0;
// Snapshots.
var snapshots = [];

benchmark.start = function(canvasToObserve) {
  canvas = canvasToObserve;
  snapshots = [];
  startTime = (new Date()).getTime();
  benchmark.snapshot();
};

benchmark.snapshot = function() {
  var startSnapshotTime = (new Date()).getTime();
  snapshots.push({
    'time': startSnapshotTime - startTime,
    'data': canvas.getContext('2d').getImageData(0, 0, canvas.width, canvas.height)
  });
  startTime += (new Date()).getTime() - startSnapshotTime;
};

benchmark.end = function() {
  benchmark.snapshot();
  return snapshots;
};

exports.benchmark = benchmark;
})(this);