import Navbar from './components/menu';
import Sidebar from './components/Sidebar';
import Tableview from './components/Tableview';
import'./components/home.css';


export default ()=>{

    return (
        <>
            <Navbar></Navbar>
            <div className='body-container'>
                <Sidebar></Sidebar>
                <Tableview></Tableview>
            </div>
            
        </>
    );
}