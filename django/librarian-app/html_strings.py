# -*- coding: utf-8 -*-

basic_response = '''
    <h1 align='center'>Welcome to LibrEasy</h1>
    <h2 align='center'>A quick and complete library management solution for librarians</h2>
    <style>
        table.t1 tr:nth-child(even) {
            background-color: #eee;
        }
        table.t1 tr:nth-child(odd) {
           background-color:#fff;
        }
        table.t1 th {
            background-color: black;
            color: white;
        }
        table.t2 td{
            border: 1px solid black;
            text-align:center;
        }
    </style>
    <table class='t2' width='80%' align='center'>
        <tr>
        <td><a href='/app'>Home</a> </td>
        <td><a href='/app/newuser'>Register</a> </td>
        <td><a href='/app/checkout'>Checkout</a></td>
        <td><a href='/app/checkin'>Checkin</a></td>
        <td><a href='/app/fines'>Fines</a></td>
        </tr>
    </table>
    <br>
'''

search_box = '''
    <h3>Instructions:</h3>
    <p>
    <b>You can enter following text in the search box below:</b><br>
    1. Name (or part of) of the author of the book,<br>
    2. Title (or part of) of the book, or<br>
    3. ISBN (or part of) of the book.
    </p>
    <h2 align='center'>Search books here:</h2>
    <form align='center' method='get'>
        <input type='text' name='query' value='{}' style='width:20%;height:30px;border-radius:4px;font-size:15px;text-align:center;background-color:#eee'>
        <input type='submit' value='Search books'>
    </form>
'''

search_table_begin = '''

    <form method='get' action='/app/checkout/'>

        <div style="height:300px;overflow:auto;border-style:groove;width:100%;" align='center'>
        <table class='t1' style='width:100%'>
            <tr align='center'>
                <th>Checkout</th>
                <th>S. No.</th>
                <th>ISBN10</th>
                <th>Book Title</th>
                <th>List of Authors</th>
                <th>String Hits</th>
                <th>Available</th>
            </tr>
'''

search_table_entry = '''
            <tr>
                <td align='center'><input type='radio' name='issue' value='{0}' {7}/></td>
                <td>{1}</td>
                <td>{2}</td>
                <td>{3}</td>
                <td>{4}</td>
                <td align='center'>{5}</td>
                <td align='center'>{6}</td>
            </tr>
'''

search_table_end = '''
        </table>
        </div>
        <br>
        <input type='submit' value='checkout' align='right'>
    </form>
'''

add_new_user = '''
    <h3><b>Please enter new user information below:</b></h3><br>
    <div align='center'>
    <form method='get'  style='width:60%'>
        <fieldset align='left'>
            <legend>Personal information</legend>
            <br>
            
            Social Security Number:
            <span style='padding-left:10px'/>
            <input type='text' maxlength='3' size='3' name='ssn1' required style='padding:0px 10px 0px 10px'> - 
            <input type='text' maxlength='2' size='2' name='ssn2' required style='padding:0px 10px 0px 10px'> -
            <input type='text' maxlength='4' size='4' name='ssn3' required style='padding:0px 10px 0px 10px'>
            <br>
            <br>
            
            First Name:
            <span style='padding-left:10px'/>
            <input type='text' name='fname' required>
            <span style='padding-left:30px'/>
            
            Middle Name:
            <span style='padding-left:10px'/>
            <input type='text' name='mname'>
            <span style='padding-left:30px'/>
            
            Last Name:
            <span style='padding-left:10px'/>
            <input type='text' name='lname' required>
            <br>
            <br>
        </fieldset>
        <br>
        <br>
        <fieldset align='left'>
            <legend>Contact details</legend>
            <br>
            
            Address:
            <span style='padding-left:10px'/>
            <input type='text' name='addr' required>
            <span style='padding-left:50px'/>
            
            City:
            <span style='padding-left:10px'/>
            <input type='text' name='city' required>
            <span style='padding-left:50px'/>
            
            State:
            <span style='padding-left:10px'/>
            
            <!-- select-list from: https://www.freeformatter.com/usa-state-list-html-select.html -->
            <select name='state' required>
                <option value="AL">Alabama</option>
                <option value="AK">Alaska</option>
                <option value="AZ">Arizona</option>
                <option value="AR">Arkansas</option>
                <option value="CA">California</option>
                <option value="CO">Colorado</option>
                <option value="CT">Connecticut</option>
                <option value="DE">Delaware</option>
                <option value="DC">District Of Columbia</option>
                <option value="FL">Florida</option>
                <option value="GA">Georgia</option>
                <option value="HI">Hawaii</option>
                <option value="ID">Idaho</option>
                <option value="IL">Illinois</option>
                <option value="IN">Indiana</option>
                <option value="IA">Iowa</option>
                <option value="KS">Kansas</option>
                <option value="KY">Kentucky</option>
                <option value="LA">Louisiana</option>
                <option value="ME">Maine</option>
                <option value="MD">Maryland</option>
                <option value="MA">Massachusetts</option>
                <option value="MI">Michigan</option>
                <option value="MN">Minnesota</option>
                <option value="MS">Mississippi</option>
                <option value="MO">Missouri</option>
                <option value="MT">Montana</option>
                <option value="NE">Nebraska</option>
                <option value="NV">Nevada</option>
                <option value="NH">New Hampshire</option>
                <option value="NJ">New Jersey</option>
                <option value="NM">New Mexico</option>
                <option value="NY">New York</option>
                <option value="NC">North Carolina</option>
                <option value="ND">North Dakota</option>
                <option value="OH">Ohio</option>
                <option value="OK">Oklahoma</option>
                <option value="OR">Oregon</option>
                <option value="PA">Pennsylvania</option>
                <option value="RI">Rhode Island</option>
                <option value="SC">South Carolina</option>
                <option value="SD">South Dakota</option>
                <option value="TN">Tennessee</option>
                <option value="TX">Texas</option>
                <option value="UT">Utah</option>
                <option value="VT">Vermont</option>
                <option value="VA">Virginia</option>
                <option value="WA">Washington</option>
                <option value="WV">West Virginia</option>
                <option value="WI">Wisconsin</option>
                <option value="WY">Wyoming</option>
            </select>
            <br>
            <br>
            
            Phone number:
            <span style='padding-left:10px'/>
            <input type='tel' name='phone'><br><br>
        </fieldset>
        <br>
        <br>
        
        <input type='submit' value='Create account'>
    </form>
    </div>
'''

new_user_card = '''
    <br>
    <div style="border:1px dotted #000;width:500px;height:280px; margin:0 auto">
    <br>
    
    <div align='center'>
    <font size=5' face='didot' color='purple'>Mc Awesome Library at UTD</font>
    <br><br><br>
    </div>
    
    <div style='padding:0px 20px 0px 20px;float:left'>
    Card ID:<br><br>
    Name:<br><br>
    SSN:<br><br>
    Phone:<br><br>
    Address:<br><br>
    </div>
    
    <div style='padding:0px 50px 0px 70px;float:left'>
    <b>{}</b><br><br>
    <b>{}</b></b><br><br>
    <b>{}</b><br><br>
    <b>{}</b><br><br>
    <b>{}</b><br><br>
    </div>
    
    <div style='float:left;border:1px solid #000;width:90px;height:90px' align='center'>
    <br><br>Affix photo here.
    </div>
    
    </div>
    <br><br>
'''


checkout_form = '''
    <h3><b>Enter book ISBN10 and user card ID to check-out a book:</b></h3><br>
    <form method='get' style='padding:0px 50px 0px 50px'>
        Enter book ISBN:
        <br>
        <input type='text' name='issue' value={0}>
        <input type='submit' name='action' value='Search book' >
        <br>
        {1}
        <br>
        Enter user ID:
        <br>
        <input type='text' name='userid' value={2}>
        <input type='submit' name='action' value='Search user'>
        <br>
        {3}
        <br>
        <input type='submit' name='action' value='Check Out'>
    </form>
'''

checkout_book_info = '''
        <font color="green">
        <b>Book ISBN:</b> {}
        <br>
        <b>Book title:</b> {}
        <br>
        </font>
'''

checkout_user_info = '''
        <font color="green">
        <b>User ID:</b> {}
        <br>
        <b>User name:</b> {}
        <br>
        </font>
'''


checkin_search_box = '''
    <h3><b>Checkin books below (use search box to find a particular entry):</b></h3>
    <form method='get' action='/app/checkin/' align='center'>
        <input type='search' name='search' value='{}' style='width:20%;height:30px;border-radius:4px;font-size:15px;text-align:center;background-color:#eee'>
        <input type='submit' name='action' value='Search'>
    </form>
'''

checkin_table_begin = '''
    
    <form>
    <table class='t1' width='100%' align='center'>
        <tr>
        <th>Select</th>
        <th>Book ISBN</th>
        <th>Issued to (ID)</th>
        <th>Issued to (name)</th>
        </tr>
'''

checkin_table_entry = '''
        <tr align='center'>
            <td><input type='radio' name='checkin' value='{0}' {4}></td>
            <td>{1}</td>
            <td>{2}</td>
            <td>{3}</td>
        </tr>
'''

checkin_table_end = '''
    </table>
    <input type='submit' name='performcheckin' value='Checkin'>
    </form>
'''























