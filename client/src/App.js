import {
  BrowserRouter as Router,
  Switch,
  Route,
  Link
} from "react-router-dom";

import Home from "./interface/pages/Home";
import Term from "./interface/pages/Term";

function App() {
  return (
      // eslint-disable-next-line react/jsx-no-undef
        <Router>
        <Switch>
          <Route path="/terminal/:session_id" component={Term} />
          <Route path="/">
            <Home />
          </Route>
        </Switch>
    </Router>
  );
}

export default App;
