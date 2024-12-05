난 슬플때 트리를 순회해.. <br>

# 원래 쓰려던 아티클
1. Go를 공부한다.
2. Splay Tree를 공부한다.
3. Go로 작성한 Splay Tree 글을 작성한다.
4. 예제를 하나 풀어보고 글로 옮긴다

# 실제로 한것 
1. Go를 공부한다.
2. Splay Tree를 공부한다.
3. 트리는 잘 동작했는데, 백준 예제 하나 풀어보려다가 그냥 하루 날림 <br> 아주 풀릴랑 말랑 해서 하루 낚여버림
4. 정리는 못했고 일단 코드만 올림.. 차차 정리하고 스플레이 트리 설명할 예정..

```go
package main

import (
	"bufio"
	"fmt"
	"math"
	"os"
)

type SplayTree struct {
	root *SplayTreeNode
}

type SplayTreeNode struct {
	key                 int64
	left, right, parent *SplayTreeNode
	size, sum, lazy     int64
}

func (node *SplayTreeNode) isNil() bool {
	return node == nil
}

func (node *SplayTreeNode) isPresent() bool {
	return node != nil
}

func (node *SplayTreeNode) updateTreeSizeAndSum() {
	node.size = 1
	node.sum = node.key

	if node.left.isPresent() {
		node.size += node.left.size
		node.sum += node.left.sum
	}

	if node.right.isPresent() {
		node.size += node.right.size
		node.sum += node.right.sum
	}
}

func (tree *SplayTree) Rotate(node *SplayTreeNode) {
	parent := node.parent
	if parent.isNil() {
		return
	}

	node.setParentToChild()
	node.setGrandParentToParent()

	if node.parent.isNil() {
		tree.root = node
	}

	// update Child Count
	node.updateTreeSizeAndSum()
	parent.updateTreeSizeAndSum()
	node.pushLazyValue()
	parent.pushLazyValue()
}

func (tree *SplayTree) Splay(node *SplayTreeNode) {
	if tree.root.isNil() || node.isNil() || node == tree.root {
		return
	}

	if node.parent == tree.root {
		tree.Rotate(node)
		return
	}

	for node.parent.isPresent() {
		parent := node.parent
		grandParent := parent.parent

		if grandParent.isPresent() {
			if checkSameDirectionChildWithParent(node) {
				// Zig-Zig
				tree.Rotate(parent)
			} else {
				// Zig-Zag
				tree.Rotate(node)
			}
		}
		// 공통 rotate 작업
		tree.Rotate(node)
	}
}

func (tree *SplayTree) GetRangeSubtreeRootWithGather(start, end int64) *SplayTreeNode {
	tree.gather(start, end)

	subtreeRoot := tree.root.right.left
	subtreeRoot.pushLazyValue()
	return subtreeRoot
}

func (tree *SplayTree) gather(start, end int64) {
	tree.GetKthNodeAndPush(end + 1)
	endNode := tree.root

	tree.GetKthNodeAndPush(start - 1)
	startNode := tree.root

	//tree.PrintDFS()
	tree.splayAndSetChild(startNode, endNode)
}

func (tree *SplayTree) splayAndSetChild(rootNode *SplayTreeNode, child *SplayTreeNode) {
	// TODO : 여기 의심
	for child.parent != rootNode && child != tree.root {
		parent := child.parent

		if parent.parent == rootNode {
			tree.Rotate(child)
			break
		}

		if checkSameDirectionChildWithParent(child) {
			// Zig-Zig
			tree.Rotate(parent)
			tree.Rotate(child)
		} else {
			// Zig-Zag
			tree.Rotate(child)
			tree.Rotate(child)
		}
	}

	child.updateTreeSizeAndSum()
	if rootNode.isNil() {
		tree.root = child
	}
}

func (tree *SplayTree) Find(key int64) *SplayTreeNode {
	//fmt.Println("Find key: ", key)
	if tree.root.isNil() {
		return nil
	}

	node, parent := tree.findNodeAndParent(key)
	if node.isPresent() {
		tree.Splay(node)
		return node
	} else {
		tree.Splay(parent)
		return nil
	}
}

func (tree *SplayTree) findNodeAndParent(key int64) (node, parent *SplayTreeNode) {
	node = tree.root
	for node.isPresent() && key != node.key {
		parent = node
		if key < node.key {
			node = node.left
		} else {
			node = node.right
		}
	}

	return node, parent
}

func (tree *SplayTree) Insert(key int64) {
	//fmt.Println("Insert key: ", key)
	if tree.root.isNil() {
		tree.root = &SplayTreeNode{key: key, size: 1, sum: key}
		return
	}

	_, parent := tree.findNodeAndParent(key)
	//if node.isPresent() {
	//	return
	//}

	newNode := &SplayTreeNode{key: key, parent: parent, size: 1, sum: key}
	if key < parent.key {
		parent.left = newNode
	} else {
		parent.right = newNode
	}
	tree.splayAndSetChild(nil, newNode)
}

func (tree *SplayTree) Delete(key int64) {
	//fmt.Println("Delete key: ", key)
	if tree.Find(key).isNil() {
		return
	}

	switch root := tree.root; true {
	case root.left.isPresent() && root.right.isPresent():
		tree.root = root.left
		tree.root.parent = nil

		node := tree.root
		for node.right.isPresent() {
			node = node.right
		}
		// 생각해보면, 왼쪽 서브 트리의 가장 오른쪽 노드는, 오른쪽 서브 트리의 루트 보다 작을 수 밖에 없다
		node.right = root.right
		root.right.parent = node

	case root.left.isPresent():
		tree.root = root.left
		tree.root.parent = nil

	case root.right.isPresent():
		tree.root = root.right
		tree.root.parent = nil

	default:
		tree.root = nil
	}
}

func (tree *SplayTree) SumRange(start, end, value int64) {
	subtreeRoot := tree.GetRangeSubtreeRootWithGather(start, end)
	tree.root.updateTreeSizeAndSum()
	if subtreeRoot.isNil() {
		return
	}
	subtreeRoot.sum += subtreeRoot.size * value
	subtreeRoot.lazy += value
}

func (tree *SplayTree) GetKthNode(k int64) int64 {
	//fmt.Printf("Get %d th Node", k)
	k -= 1
	node := tree.root
	for node.isPresent() {
		for node.left.isPresent() && node.left.size > k {
			node = node.left
		}

		if node.left.isPresent() {
			k -= node.left.size
		}

		if k == 0 {
			break
		}

		k--
		node = node.right
	}

	tree.Splay(node)
	//fmt.Printf(" -> %d\n", node.key)
	return node.key
}

func (tree *SplayTree) GetKthNodeAndPush(k int64) {
	//fmt.Printf("Get %d th Node And Push\n", k)
	//k -= 1	// 더미 떄문에 삭제
	node := tree.root
	node.pushLazyValue()

	for node.isPresent() {
		for node.left.isPresent() && node.left.size > k {
			node = node.left
			node.pushLazyValue()
		}

		if node.left.isPresent() {
			k -= node.left.size
		}

		if k == 0 {
			break
		}

		k--
		node = node.right
		if node.isPresent() {
			node.pushLazyValue()
		}
	}

	tree.Splay(node)
	//fmt.Printf(" -> %d\n", node.key)
	return
}

func (node *SplayTreeNode) pushLazyValue() {
	lazyValue := node.lazy
	node.lazy = 0

	if node.key != math.MinInt64 && node.key != math.MaxInt64 {
		node.key += lazyValue
	}

	if left := node.left; left.isPresent() {
		left.lazy += lazyValue
		left.sum += left.size * lazyValue
	}

	if right := node.right; right.isPresent() {
		right.lazy += lazyValue
		right.sum += right.size * lazyValue
	}
}

func (node *SplayTreeNode) setGrandParentToParent() {
	parent := node.parent
	grandParent := parent.parent

	// change Parent
	node.parent = grandParent
	parent.parent = node

	if node.parent.isNil() {
		return
	}

	// TODO : grandParent로 바꾸기
	if parent == node.parent.left {
		node.parent.left = node
	} else {
		node.parent.right = node
	}

	// TODO : 중복 제거
	node.updateTreeSizeAndSum()
	parent.updateTreeSizeAndSum()
}

func (node *SplayTreeNode) setParentToChild() {
	parent := node.parent
	var newChild *SplayTreeNode

	if node == parent.left {
		newChild = node.right
		parent.left = newChild
		node.right = parent
	} else {
		newChild = node.left
		parent.right = newChild
		node.left = parent
	}

	if newChild != nil {
		newChild.parent = parent
	}
}

func checkSameDirectionChildWithParent(node *SplayTreeNode) bool {
	parent := node.parent
	grandParent := parent.parent

	isNodeLeft := node == parent.left
	isParentLeft := parent == grandParent.left
	return isNodeLeft == isParentLeft
}

// print 함수
func (tree *SplayTree) PrintDFS() {
	printDFS(tree.root, 0, "root")
	fmt.Println() // 보기 편하려고 넣음
}

func printDFS(node *SplayTreeNode, level int, direction string) {
	if node.isNil() {
		return
	}

	fmt.Printf("%s[%s] : Node %d\n", getIndent(level), direction, node.key)

	printDFS(node.left, level+1, "left")
	printDFS(node.right, level+1, "right")
}

// 출력 시 들여쓰기를 위한 함수
func getIndent(level int) string {
	indent := ""
	for i := 0; i < level; i++ {
		indent += "  "
	}
	return indent
}

func main() {
	reader := bufio.NewReader(os.Stdin)
	writer := bufio.NewWriter(os.Stdout)

	var N, M, K int
	//fmt.Fscanf(reader, "%d %d %d", &N, &M, &K)
	fmt.Fscanln(reader, &N, &M, &K)

	tree := &SplayTree{root: nil}
	tree.Insert(math.MinInt64)
	for i := 0; i < N; i++ {
		var value int64
		//fmt.Fscanf(reader, "%d", &value)
		fmt.Fscanln(reader, &value)
		//fmt.Println(value)
		tree.Insert(value)
	}
	tree.Insert(math.MaxInt64)

	const (
		SUM     = 1
		GET_SUM = 2
	)

	for i := 0; i < M+K; i++ {
		var command, start, end, value int64
		//fmt.Fscanf(reader, "%d %d %d", &command, &start, &end)
		fmt.Fscanln(reader, &command, &start, &end, &value)
		//fmt.Printf("%d %d %d %d\n", command, start, end, value)

		switch command {
		case SUM:
			//fmt.Fscanf(reader, "%d", &value)
			tree.SumRange(start, end, value)
			//fmt.Fprintf(writer, "%d %d %d %d\n", command, start, end, value)

		case GET_SUM:
			subtreeRoot := tree.GetRangeSubtreeRootWithGather(start, end)
			fmt.Fprintf(writer, "%d\n", subtreeRoot.sum)
			//fmt.Println(subtreeRoot.sum)
			//fmt.Fprintf(writer, "%d %d %d %d\n", command, start, end, value)
		}
	}

	writer.Flush()
}

```
