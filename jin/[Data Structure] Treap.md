# Treap

Treap이란, Tree 형태로 구현된 Heap으로 Tree + Heap 이라서 Treap이다. <br>
기본적으로, 노드들이 다음 노드를 가르키는 형태의 연결 리스트 혹은 트리현 자료구조들은, 
노드들이 선형과 가까이 놓이게 되면 탐색 시간 복잡도가 O(N)까지 느려진다. <br>
이러한 치우침을 피하기 위해 균형 잡힌 트리 - Balanced Binary Search Tree 들은 
깊이가 너무 깊어지지 않도록 균형을 맞추고, 대체로 O(logN)의 시간 복잡도를 보장한다. <br> <br>

Treap은 "확률적"인 BST로, Heap과 같이 "자식노드는 부모 노드 보다 우선 순위가 낮다." 라는 규칙을 지키는 이진 트리라는 점에서 Heap과 거의 비슷하지만, 각 노드들의 우선순위 값이 랜덤으로 주어진다! <br>
또한 BST이기 때문에, 부모 노드에서 자식 노드로 이동할 때 더 작은 숫자인 경우 왼쪽으로, 더 큰 숫자인 경우 오른쪽으로 이동한다. (너무 대충 말했는데, BST에 관한 이야기이므로 이해했기를 기대한다..) <br>
노드가 삽입될 때마다 랜덤한 우선순위가 주어지고, 그 우선순위에 따라 트리에 삽입된다. <br>
만약 루트 보다 우선 순위가 높은 노드가 삽입된다면 루트는 자식 노드가 되는 식이다. <br>
이러한 "확률적"인 자료구조인 Treap은 평균적으로 O(logN)의 탐색 시간 복잡도를 보인다. <br>
아주 낮은 확률로 O(N)의 시간 복잡도에 동작할 수도 있지만, 이는 매우 낮은 확률이다.

<br> <br>

이러한 Treap이 좋은 이유는 BBST와 거의 비슷한 시간 복잡도를 보이면서 구현이 아주 간단하다는 것이다. <Br>
Heap을 구현하는 정도의 난이도인데, 다른 BBST들을 생각해보면.. (AVL Tree, Red-Black Tree 등..) 선녀인 것이다.


## 1. Treap Insert
이제 Treap의 삽입을 알아보자.
1. 노드의 우선순위는 랜덤으로 주어진다.
2. BST에 값을 넣는 방식대로 들어가게 될 위치를 찾아 삽입하면 된다.
3. 새 노드가 기존 노드보다 우선순위가 높은 경우 Split한다.

```go
func (treap *Treap) Insert(key int, value Value) {
    root := treap.root
    newNode := treap.NewNode(key, value)
    treap.root = treap.insert(root, newNode)
}

func (treap *Treap) insert(current, newNode *Node[Value]) *Node[Value] {
	// 1. Root가 Null인 경우 newNode가 set될 수 있도록 newNoe
    if current == nil {
        return newNode
    }
	
	//2. 새로운 노드가 Root 보다도 우선순위가 높은 경우, 새로운 노드를 루트로 둔다.
    if current.priority < newNode.priority {
        left, right := treap.split(current, newNode)
        newNode.left = left
        newNode.right = right
        return newNode
    }

	// 3. 새로운 노드가 Root 보다도 우선순위가 낮은 경우, 새로운 노드를 root의 자식으로 둔다.
    if newNode.key < current.key {
        insert := treap.insert(current.left, newNode)
        current.setLeft(insert)
        return current
    }
    insert := treap.insert(current.right, newNode)
    current.setRight(insert)
    return current
}

// 재귀적인 Split
func (treap *Treap) split(baseNode, newNode *Node[Value]) (*Node[Value], *Node[Value]) {
    if baseNode == nil {
        return nil, nil
    }
    
    if baseNode.key < newNode.key {
        left, right := treap.split(baseNode.right, newNode)
        baseNode.setRight(left)
        return baseNode, right
    } 
    left, right := treap.split(baseNode.left, newNode)
    baseNode.setLeft(right)
    return left, baseNode
}
```

<br>

재귀적인 split이 복잡하므로, 그림으로 그려 보았다. <br>
아래 트리에서 8이라는 key를 가진 노드가 삽입되는데, 우선순위가 기존 Root 보다 높은 상황을 그려보았다.

![insert 1](https://github.com/user-attachments/assets/a2a07d37-d6f3-4803-a404-d4ac4177bf30)

![insert 2](https://github.com/user-attachments/assets/d387e18e-6bbb-4088-af9f-129dcebdaed6)

![insert 3](https://github.com/user-attachments/assets/0892c889-8268-475c-8bf5-f30dd2d9ff31)

![insert 4](https://github.com/user-attachments/assets/79aa2492-9290-4d89-9a6a-fac90991f9d6)

<br>

### Split 4는 생략했다. 9의 자식이 전부 nil을 가리키기 때문에, (nil, nil)을 반환한다.

<br> <br>

![insert 5](https://github.com/user-attachments/assets/51bc8f2e-2eb7-4a41-92ba-810dfcd37bc1)

![insert 6](https://github.com/user-attachments/assets/7e1d4012-eb42-4aad-bd54-321a145bac96)

![insert 7](https://github.com/user-attachments/assets/adf227af-453a-4eb9-bcbd-05fd0ab83d94)

<br> <br>


## 2. Treap Remove
```go
func (treap *Treap) Remove(key int) {
	treap.remove(treap.root, key)
}

func (treap *Treap) remove(baseNode *Node[Value], key int) (returnNode *Node[Value]) {
	returnNode = baseNode
	if treap.root == nil {
		return
	}

	if baseNode.key == key {
		merge := treap.merge(baseNode.left, baseNode.right)
		baseNode = nil
		returnNode = merge
	} else if key < baseNode.key {
		baseNode.left = treap.remove(baseNode.left, key)
	} else {
		baseNode.right = treap.remove(baseNode.right, key)
	}
	return
}

func (treap *Treap) merge(left, right *Node[Value]) *Node[Value] {
	if left == nil {
		return right
	}

	if right == nil {
		return left
	}

	if left.priority < right.priority {
		right.left = treap.merge(left, right.left)
		return right
	}

	left.right = treap.merge(left.right, right)
	return left
}
```

<br> <br>

## 3. Treap Find
find는 쉽다. K번째 노드를 찾는 코드이다.

```go
func (treap *Treap) Find(index int) *Node[Value] {
	return treap.find(treap.root, index)
}

func (treap *Treap) find(nodeNow *Node[Value], index int) *Node[Value] {
	leftSize := 1
	if nodeNow.left != nil {
		leftSize += nodeNow.left.size
	}

	if index == leftSize {
		return nodeNow
	}

	// 왼쪽으로 이동
	if index < leftSize {
		return treap.find(nodeNow.left, index)
	}
	// 오른쪽으로 이동
	return treap.find(nodeNow.right, index-leftSize)
}
```

특정 인덱스의 노드를 찾을 것이다.
왼쪽 서브 트리의 노드 갯수와 현재 노드를 더한 `leftSize`가 현재 노드의 인덱스이다.
만약 내가 찾는 인덱스와 값이 같다면 노드를 찾은 것이고, 아니라면 다른 노드로 이동한다.
만약 찾는 인덱스 값이 `leftSize`보다 작다면 왼쪽으로 이동할 것이다.
그리고 leftSize보다 내가 찾는 인덱스가 더 크다면 오른쪽으로 이동하는데, `leftSize` 만큼을 index에서 뺀다.
그러면 이제 오른쪽 자식 노드가 탐색할 새로운 트리의 루트이고, 내가 찾는 노드의 인덱스는 `index - lifeSize`인 것이다.


[//]: # (## 높이 증명)

[//]: # ()
[//]: # (노드가 N개인 어떤 Treap에서 특정 노드를 찾을 때의 시간 복잡도가 O&#40;logN&#41;임을 증명한다.)

[//]: # (Root 부터 Treap을 탐색하는 경우를 생각해보자.)

[//]: # (현재 탐색중인 노드를 "현재 노드"라고 부르겠다.)

[//]: # (예를 들어 루트에서 왼쪽으로 탐색하기 위해 왼쪽 자식 노드로 이동했다면, 이제 왼쪽 자식 노드가 "현재 노드"이다.)

[//]: # ()
[//]: # (1. 현재 노드는 서브 트리 내의 루트 노드로써, 서브 트리 내의 노드들 중 최대의 우선순위를 가짐이 명백하다.)

[//]: # (2. 서브 트리의 모든 노드를 오름차순으로 정렬했다고 생각해봤을 때, 서브 트리의 루트 &#40;현재 노드&#41;가 가진 숫자가 k번째 번째 숫자라고 생각해보자.)

[//]: # (   그러면 왼쪽 자식 노드가 루트인 서브 트리는 k-1개의 숫자가 있고, 오른쪽 자식이 루트인 서브 트리에는 N-k개의 숫자가 있을 것이다.)

[//]: # (3. 우리가 찾는 노드가 왼쪽에 있을 확률은 &#40;k-1&#41;/N, 오른쪽에 있을 확률은 &#40;N-k&#41;/N, 현재 노드인 확률은 1/N일 것이다.)

[//]: # (4. 이번 단계에서 )
