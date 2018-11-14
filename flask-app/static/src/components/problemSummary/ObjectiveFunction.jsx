import React from 'react';
import MathJax from 'react-mathjax2';

class ObjectiveFunction extends React.Component {
  render() {
    let { varNum } = this.props.objFun;
    const tex = `\\sum_{i=1}^{${varNum}}c_ix_i`;
    return (
      <div>
        <MathJax.Context input="tex">
          <div>
            <MathJax.Node>{tex}</MathJax.Node>
          </div>
        </MathJax.Context>
      </div>
    );
  }
}

export default ObjectiveFunction;
