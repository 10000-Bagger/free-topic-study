# Filtering Data in React Query Like a Pro

참고 자료: https://betterprogramming.pub/filtering-data-in-react-query-like-a-pro-ec481b53b515

## Filtering data on the Server

### Problem Statement

- 직원들의 인사 데이터를 배열 형식으로 서버에서 응답을 받았다고 가정.
- 이 API는 2개의 param을 가지고 있음.
    - position, name
- 이 API는 요청되는 query param에 따라 데이터를 필터링을 수행함.
- param이 없는 경우, 전체 데이터를 전달.
- 예시 데이터:

```tsx
// GET /api/v1/employees?positions=:positions&name=:name
[{
    name: '권우석',
    birthdatte: '1975-02-28',
    position: 'regional_manager',
    yearly_salary: 100000,
    active: true
},
{
    name: '이진호',
    birthdatte: '1980-02-12',
    position: 'assistant_to_regional_manager',
    yearly_salary: 70000,
    active: true
},
{
    name: '허준영',
    birthdatte: '1982-04-02',
    position: 'salesman',
    yearly_salary: 70000,
    active: true
},
{
    name: '신민경',
    birthdatte: '1970-07-18',
    position: 'salesman',
    yearly_salary: 65000,
    active: true
},
{
    name: '류홍석',
    birthdatte: '1984-05-28',
    position: 'salesman',
    yearly_salary: 60000,
    active: true
}];
```

### Solution

- 자동으로 처리될 . 수있는 이러한 기능을 만들기 위해서는 react-query에서 제공하는 refetch를 사용하면 된다.
- react-query는 query-key를 사용해서 cached 데이터를 API로 부터 fetch 한다.

```tsx
export const useGetEmployees = () => {
  return useQuery(['employees'], () => fetchEmployees());
}

const SomeComponent = () => {
const { data } = useGetEmployees();
```

- Query-key가 업데이터 될 때 refetch할 data는 자동으로 Trigger 된다. 그렇기 때문에 query-key에 이미 필터된 데이터를 추가하여 해당 기능을 활용할 수 있다.
- 필터된 데이터가 업데이트 되면 자동으로 API가 호출되고, 필터된 데이터를 다시 서버로부터 받아볼 수 있다.

```tsx
export const useGetEmployees = (filters) => {
  // Everytime your filters change, react-query will refetch data.
  // if your filters don't change, your data will remain cached.
  return useQuery(['employees', filters], () => fetchEmployees(filters)); 
};

const SomeComponent = () => {
  const [filters, setFilters] = useState({});
  const { data } = useGetEmployees(filters);
  
  const onChange = (values) =>{
    setFilters(value)
  }
  
  // return component ...
}
```

- 저장된 필터의 값이 변경된다면 해당 function이 호출될 것이고 아니면 저장된 값을 사용한다.

여기까지는 문제가 없다. 

### 그런데 filtered 데이터를 수정한다면?

filtered 데이터 하나를 수정한다면 다른 필더가 적용된 캐싱 데이터는 어떻게 처리해야할까?

현재 보고 있는 페이지는 캐시 값을 수정하고, 전체 조회 query만 stale 상태로 변경할 수 있을까?

아니면 현재 변경한 row의 id 값이 포함된 cache의 query만 stale 상태로 변경할 수 있을까?

위와 같은 상황에 대한 대처를 하기 위해 react-query의 query invalidation 문서를 확인했다.

https://tanstack.com/query/v4/docs/framework/react/guides/query-invalidation

## Query Invalidation

> Waiting for queries to become stale before they are fetched again doesn’t always work, especially when you know for a fact that a query’s data is out of date because of something the use has done. For that purpose, the `QueryClient` has an `invalidateQueries` method that lets you intelligently mark queries as stale and potentially refetch them too!
> 

invalidateQueries를 현명하게 사용하는 방법을 알아본다.

### 방법 1: query-key 이름으로 invalidate

- 가장 기본적으로 사용하는 방식

```tsx
// invalidate every query with a key that stats with 'todos'
queryClient.invalidateQueryies({ queryKey: ['todos'] })

// Both queries below will be invalidated
const todoListQuery = useQuery({
  queryKey: ['todos'],
  queryFn: fetchTodoList,
})
const todoListQuery = useQuery({
  queryKey: ['todos', { page: 1 }],
  queryFn: fetchTodoList,
})
```

- 해당 함수가 실행되면 아래 두개의 작업이 수행된다.
- stale 상태로 변경 (The stale overrides as `staleTime` configurations being used in `useQuery` or related hooks)
- If the queryis currently being rendered via `useQuery` or related hooks, it will also be refetched in the background

### 방법 2: Query Matching

- invalidateQueries, removeQuerises 등은 query matching 기능을 제공한다.
- query matching 기능을 사용해서 조건절로 사용할 수 있는 모든 로직을 수행할 수 있다.

```tsx
queryClient.invalidateQueries({
  queryKey: ['todos', { page: 1 }],
})

// The query below will be invalidated
const todoListQuery = useQuery({
  queryKey: ['todos', { page: 1 }],
  queryFn: fetchTodoList,
})

// However, the following query beflow will NOT be invalidated
const todoListQuery = useQuery({
  queryKey: ['todos'],
  queryFn: fetchTodoList,
})
```

- filter가 없는 전체리스트를 가져오는 쿼리를 수정하고 싶은 경우, `exact` 옵션을 사용하면 된다.

```tsx
queryClient.invalidateQueries({
  queryKey: ['todos'],
  exact: true,
})

// The query below will be invalidated
const todoListQuery = useQuery({
  queryKey: ['todos'],
  queryFn: fetchTodoList,
})

// However, the following query below will NOT be invalidated
const todoListQuery = useQuery({
  queryKey: ['todos', { page: 1 }],
  queryFn: fetchTodoList,
})
```

- 더 세분화된 조건을 설정하고 싶은 경우, `predicte` 옵션을 사용하면 된다.
- `predicte` 옵션은 query cache 데이터에서 모든 `Query` instance를 가져와서 조건절의 결과로 invalidate 대상 query를 선택할 수 있다.

```tsx
queryClient.invalidateQueries({
  predicate: (query) =>
    query.queryKey[0] === 'todos' && query.queryKey[1]?.page == 1,
})

// The query below will be invalidated
const todoListQuery = useQuery({
  queryKey: ['todos'. { page: 1 }],
  queryFn: fetchTodoList, 
})

// However, the following query below will NOT be invalidated
const todoListQuery = useQuery({
  queryKey: ['todos'],
  queryFn: fetchTodoList,
})
```

### 정리

react-query에서 제공하는 query matching과 [Query Filters](https://tanstack.com/query/latest/docs/framework/react/guides/filters#query-filters)를 잘 사용하면, filter 키워드와 페이지를 기준으로 관련 데이터를 뽑아서 수정하는 것도 가능할 것이라 생각했는데… ~~setQueryData 함수에는 필터 기능을 사용할 수 없다는 것을 알게 됐다.. ?~~ 인줄 알았지만 QueryClient class를 확인해보니 setQueriesData로 QueryFilter를 사용할 수 있더라…

```tsx
// QueryClient 옵션
declare class QueryClient {
  // ..
  getQueriesData<TQueryFnData = unknown>(filters: QueryFilters): Array<[QueryKey, TQueryFnData | undefined]>;
  setQueriesData<TQueryFnData>(filters: QueryFilters, updater: Updater<TQueryFnData | undefined, TQueryFnData | undefined>, options?: SetDataOptions): Array<[QueryKey, TQueryFnData | undefined]>;
  removeQueries(filters?: QueryFilters): void;
  invalidateQueries(filters?: InvalidateQueryFilters, options?: InvalidateOptions): Promise<void>;
  refetchQueries(filters?: RefetchQueryFilters, options?: RefetchOptions): Promise<void>;
}
```

위 처럼 QueryFilter 옵션이 있는 경우, predicate와 같이 조건절에 따른 cache 데이터 처리가 가능하다.

- 하지만 filter & pagination 조합인 경우, (filter가 적용된 페이지 x 페이지별로 변경된 row가 들어있는지 확인)해야하는 문제가 있음.
- pagination된 페이지이기 때문에 해당 페이지를 업데이트 때마다 refetch해도 크게 문제가 되지 않을 것으로 판단, 결국은 관련된 모든 cache를 invalidate하는 방식으로 적용함...
