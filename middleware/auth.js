import Router from 'next/router'

export function withAuth(Component) {
  return function WithAuth(props) {
      Router.push('/login')
      return null
  }
}
