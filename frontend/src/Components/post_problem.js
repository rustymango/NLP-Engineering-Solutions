import axios from 'axios'
import React, { Component } from 'react'
import './component1.css'

class PostProblem extends Component {
    constructor(props) {
        super(props)

        this.state = {
            problem: "",
            // calculation_steps: "",
            // answer: ""
            calculations: []
        }
    }

    problemhandler = (event) => {
        this.setState({
            problem: event.target.value
        })
    }

    componentDidMount() {
        axios
        
            .get("http://127.0.0.1:5000/calculations")
            .then(res => {
                this.setState({ calculations: res.data });
            })
            .catch(err => {
                console.error(err);
            });
    }

    handleSubmit = async (event) => {
        event.preventDefault()

        if (this.state.calculations.length > 0) {
            this.state.calculations.forEach(async rank => {

            await axios.delete(`http://127.0.0.1:5000/calculations/${rank.id}`)
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
        // const {weight, gender, age} = this.state

        return (
            <div>
                <form onSubmit={this.handleSubmit }>
                    <h1>Lifting Class Registration</h1>
                    <label>Enter Problem: </label> <input type="text" value={this.state.problem} onChange={this.problemhandler} placeholder="Problem..." /><br />
                    <button onClick={this.handleSubmit}>Submit</button>
                </form>
            </div>
        )
    }

}

export default PostProblem