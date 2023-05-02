import axios from "axios"

import './App.css';
import PostCalculations from "./Components/post_answer";
import PostProblem from "./Components/post_problem";

const baseUrl = "http://localhost:5000"

function App() {
  return (
    <div className="App">
      <PostProblem />
      <PostCalculations />  
    </div>
  );
}

export default App;
