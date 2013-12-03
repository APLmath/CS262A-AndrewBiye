/**
 * qualityeval.js provides functions to evaluate the fidelity of snapshots.
 *
 * Please include the following scripts for this to work:
 * <script type="text/javascript" src="http://canvg.googlecode.com/svn/trunk/rgbcolor.js"></script> 
 * <script type="text/javascript" src="http://canvg.googlecode.com/svn/trunk/StackBlur.js"></script>
 * <script type="text/javascript" src="http://canvg.googlecode.com/svn/trunk/canvg.js"></script> 
 *
 * For each evaluation function:
 *
 * Parameter:
 * [{
 *   time: snapshot time
 *   svg:  the SVG snapshot
 * }*]
 *
 * Returns:
 * [{
 *   time:    snapshot time
 *   quality: value between 0 and 1, 1 being perfect
 * }*]
 */

qualityeval = (function() {
var qualityeval = {};

/**
 * Measures the pixel difference between a given snapshot and the final snapshot.
 */
qualityeval.absPixelDiff = function(snapshots) {
  var serializer = new XMLSerializer();
  function getImageData(svg) {
    var canvas = document.createElement('canvas');
    canvg(canvas, serializer.serializeToString(svg));
    return canvas.getContext('2d').getImageData(0, 0, canvas.width, canvas.height);
  }

  var finalImageData = getImageData(snapshots[snapshots.length - 1].svg);
  function getImageDiff(imageData) {
    var totalDiff = 0;
    for (var i = 0; i < imageData.data.length; i++) {
      totalDiff += Math.abs(finalImageData.data[i] - imageData.data[i]);
    }
    return totalDiff;
  }

  qualities = [];
  var originalDiff = getImageDiff(getImageData(snapshots[0].svg))
  for (var i = 0; i < snapshots.length; i++) {
    var snapshot = snapshots[i];
    qualities.push({
      time: snapshot.time,
      quality: 1 - Math.min(1, getImageDiff(getImageData(snapshot.svg)) / originalDiff)
    });
  }

  return qualities;
};

return qualityeval;
})();