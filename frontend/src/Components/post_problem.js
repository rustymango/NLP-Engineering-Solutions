import axios from 'axios'
import React, { Component } from 'react'
import './component1.css'

class PostProblem extends Component {
    constructor(props) {
        super(props)

        this.state = {
            problem: "",
            calculations: []
        }
    }

    problemhandler = (event) => {
        this.setState({
            problem: event.target.value
        })
    }

    async componentDidMount() {
        this.setState({ loading: true }); // set loading state to true before making API request
        const response = await fetch('http://127.0.0.1:5000/calculations'); // make API request
        const data = await response.json();
        this.setState({ calculations: data.calculations, loading: false }); // update both calculations and loading state
      }

    handleSubmit = async (event) => {
        event.preventDefault()
        console.log(this.state.calculations.length)

        if (this.state.calculations.length > 0) {
            this.state.calculations.forEach(async calculation => {

            await axios.delete(`http://127.0.0.1:5000/calculations/${calculation.id}`)
            await axios.post("http://127.0.0.1:5000/calculations", this.state)
                .then(response => {
                    console.log(response)
                    window.location.reload()
                })
                .catch(error =>{
                    console.log(error.response)
                })
            });
        }

        else {
        axios

            .post("http://127.0.0.1:5000/calculations", this.state)
            .then(response => {
                console.log(response)
                window.location.reload()
            })
            .catch(error =>{
                console.log(error.response)
            })

        console.log(this.state);
        this.setState({
            problem: "",
        })
        }
    }

    render() {

        return (
            <div>
                <form onSubmit={this.handleSubmit }>
                    <h1>ENGINEERING CALCULATOR</h1>
                    <h3>Please enter your design problem specifying material type and given design parameters.
                        The values provided do not have to be in a specific unit; however, all provided answers will be in metric.
                        The tool is capable of standard formula calculation and back calculation.</h3>
                    <h2>Enter Problem: </h2> 
                    <textarea value={this.state.problem} onChange={this.problemhandler} placeholder="Problem..."></textarea>
                    <br />
                    <button onClick={this.handleSubmit}>Calculate!</button>
                </form>
            </div>
        )
    }

}

export default PostProblem