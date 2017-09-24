import React from 'react'
import ReactDOM from 'react-dom'

import { getQueryParameterByName, } from './utils/query';

import { connectSocket, } from './store'

import CreateNewList from './components/create_new_list'
import Page from './components/page'

import './styles/index.scss'

// Connect store to server via socket.io
connectSocket()

// Obtain the listId from the query parameters.
const listId = Number(getQueryParameterByName('q')) || null

ReactDOM.render(
  <div>
    { listId ? <Page listId={ listId } /> : <CreateNewList /> }
  </div>,
  document.getElementById('app')
)