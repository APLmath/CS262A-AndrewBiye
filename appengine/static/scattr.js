(function(exports) {
// Scattr relies on D3, so check for that first.
if (!d3) {
  console.log('Please include the D3 library first.')
  return;
}

// Constructor.
var Scattr = function(dataId) {
  this.dataId_ = dataId;
};

// Make Scattr available to use.
exports.Scattr = Scattr;
})(this);