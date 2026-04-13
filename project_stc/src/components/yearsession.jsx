import { useParams } from "react-router-dom"

export default ()=>{
    const params = useParams();
    const year = params.year || 'None';
    console.log(params);
    return (
        `session ${params.year}`
    )
}