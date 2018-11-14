import React from 'react';

import ProblemSummary from './problemSummary/ProblemSummary.jsx';
import Editor from './editor/Editor.jsx';

class App extends React.Component {
  state = {
    objFun: {
      varNum: 1,
      varCon: [1],
      probType: 'max'
    },
    varNum: 1,
    probType: 'max',
    constNum: 1
  };

  render() {
    let { objFun, probType, constNum } = this.state;
    return (
      <div>
        <Editor />
        <ProblemSummary objFun={objFun} probType={probType} constNum={constNum} />
      </div>
    );
  }
}

export default App;
