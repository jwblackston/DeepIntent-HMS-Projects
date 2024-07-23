#PMATool_Ver6

PMATool_Ver6 is a Python based tool to help Boris with some of the manual PMA tasks. This tool is implemented using streamlit. The script takes in a PMA dry run , PMA audience statistics file and the cohort seed size.The analyzer first finds the estimated audience size based on the seed size using an internal list. Second the the estimated audience size is index is found in the dry run file to get the threshold. The threshold found is then matched in the audience statistics file to submit in the ticket for the client. Additionally the user can manually search/edit the output at the end of the initial process if needed. 

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install streamlit.

```
-- pip install streamlit
```
More information can be found at https://streamlit.io/ 
## Usage 

To run the tool in console . Additionally make sure all files are in the path ! 
```
streamlit run 'PMATool_Ver6_Streamlit.py' 
```