import React from 'react';
import MathJax from 'react-mathjax2';

import ObjectiveFunction from './ObjectiveFunction.jsx';

class ProblemSummary extends React.Component {
  render() {
    let { objFun, probType, constNum } = this.props;
    return (
      <div>
        <ObjectiveFunction objFun={objFun} />
      </div>
    );
  }
}

export default ProblemSummary;
