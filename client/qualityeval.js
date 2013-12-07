/**
 * qualityeval.js provides functions to evaluate the fidelity of snapshots.
 *
 * For each evaluation function:
 *
 * Parameter:
 * [{
 *   time:   snapshot time
 *   canvas: the image data of the canvas
 * }*]
 *
 * Returns:
 * [{
 *   time:    snapshot time
 *   quality: value between 0 and 1, 1 being perfect
 * }*]
 */

(function(exports) {
var qualityeval = {};

/**
 * Measures the pixel difference between a given snapshot and the final snapshot.
 */
qualityeval.absPixelDiff = function(snapshots) {
  var finalImageData = snapshots[snapshots.length - 1].data;
  function getImageDiff(imageData) {
    var totalDiff = 0;
    for (var i = 0; i < imageData.data.length; i++) {
      totalDiff += Math.abs(finalImageData.data[i] - imageData.data[i]);
    }
    return totalDiff;
  }

  qualities = [];
  var originalDiff = getImageDiff(snapshots[0].data)
  for (var i = 0; i < snapshots.length; i++) {
    var snapshot = snapshots[i];
    qualities.push({
      time: snapshot.time,
      quality: 1 - Math.min(1, getImageDiff(snapshot.data) / originalDiff)
    });
  }

  return qualities;
};

exports.qualityeval = qualityeval;
})(this);