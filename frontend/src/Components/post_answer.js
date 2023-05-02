import axios from 'axios';
import React, { Component, useState, useEffect } from 'react';
// import { useParams } from 'react-router-dom';

function PostCalculations () {

    var postFromResponse = null;
    const [calculations, setCalculations] = useState([]);
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    function fetchCalculations () {

    setLoading(true);
    axios
    
        .get("http://127.0.0.1:5000/calculations")
        .then(response => response.data)
        .then((data) => {
            setCalculations(data.calculations)
            console.log(data)

        })
        .catch((error) => {
            setError(error.message);
        })
        .finally(() => {
            setLoading(false);
        })
    }

    useEffect(() => {
        fetchCalculations();
    }, [])


    const table = {
        margin: '0 auto',
        padding: '0px 0px 5px 0px',
        width: '80%'
    }

    const td ={
        padding: '0px 0px 20px 0px'
    }

    const align ={
        textAlign: 'justify'
    }

    if (calculations?.length > 0) {
        console.log(calculations?.length)
        return(
            <div>
                <h1>Calculation Steps + Answer</h1>
                <table style = {table}>
                    <thead>
                        <tr>
                            <th>Test</th>
                        </tr>
                    </thead>
                    <tbody>
                    {
                        calculations.map(calculation =>
                            <tr key = {calculation.id}>
                                <td style={td}> {calculation.calculation_steps} </td> 
                                <td style={td}> {calculation.answer} </td> 
                            </tr>
                        )
                    }
                    </tbody>
                </table>
            </div>
        )
    }
    else {
        console.log(calculations?.length)
        return(
            <div>
                <h3>-.-----------</h3>
            </div>
        )
    }

};

export default PostCalculations