import React from 'react';
import { useAsyncDebounce} from 'react-table'
import { BsSearch } from "react-icons/bs";


function SearchBar({
    globalFilter,
    setGlobalFilter,
  }) {
    const [value, setValue] = React.useState(globalFilter)
    const onChange = useAsyncDebounce(value => {
      setGlobalFilter(value || undefined)
    }, 200)
  
    return (
    <div>
        <label htmlFor="all-patients-filter-input"  className="sr-only" >Filter</label>
        <div className="input-group">
            <div className="input-group-addon"><BsSearch /></div>
            <input 
                value={value || ""}
                onChange={e => {
                    setValue(e.target.value);
                    onChange(e.target.value);
                }}
                type="text" 
                id="all-patients-filter-input" 
                placeholder="Filter by patient name" 
                className="form-control" 
            />
        </div>
    </div>
    );
}

export default SearchBar;