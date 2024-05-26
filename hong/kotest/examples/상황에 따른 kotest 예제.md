# 상황에 따른 Kotest 예제

## basic

> 테스트 스타일에 따른 테스트 케이스 예제:
> 

### Behavior

- 명확한 User Story 또는 Acceptance Criteria가 있는 경우 이를 바탕으로 작성함으로써 test case 작성 비용을 감소하고 제품 이해도를 증가시킬 수 있음.

```kotlin
class CalculatorBehaviorTest : BehaviorSpec({
    val calculator = Calculator()

    Given("0이 아닌 피연산자가 주어지고") {
        val operand1 = 10
        val operand2 = 5
        When("덧셈을 요청하면") {
            val result = calculator.add(operand1, operand2)
            Then("결과 값이 올바르게 나와야 한다.") {
                result shouldBe 15
            }
        }

        When("뺄셈을 요청하면") {
            val result = calculator.subtract(operand1, operand2)
            Then("결과 값이 올바르게 나와야 한다.") {
                result shouldBe 5
            }
        }

        When("곱셈을 요청하면") {
            val result = calculator.multiply(operand1, operand2)
            Then("결과 값이 올바르게 나와야 한다.") {
                result shouldBe 50
            }
        }

        When("나눗셈을 요청하면") {
            val result = calculator.divide(operand1, operand2)
            Then("결과 값이 올바르게 나와야 한다.") {
                result shouldBe 2
            }
        }
    }

    Given("우측 피연산자가 0으로 주어지고") {
        val operand1 = 10
        val operand2 = 0
        When("곱셈을 요청하면") {
            val result = calculator.multiply(operand1, operand2)
            Then("결과 값이 0으로 출력되야 한다.") {
                result shouldBe 0
            }
        }

        When("나눗셈을 요청하면") {
            val exception = shouldThrow<ArithmeticException> {
                calculator.divide(operand1, operand2)
            }
            exception.message shouldBe "/ by zero"
        }
    }
})
```

### Describe

- 테스트 대상이 분기를 가지고 있어 여러 조건에서 테스트를 작성해야 할 때 유용.

```kotlin
class CalculatorDescribeTest : DescribeSpec({
    val calculator = Calculator()

    describe("add test") {
        it("10 + 5는 15가 되어야 한다.") {
            calculator.add(10, 5) shouldBe 15
        }
    }

    describe("subtract test") {
        it("10 - 5는 5가 되어야 한다.") {
            calculator.subtract(10, 5) shouldBe 5
        }
    }

    describe("multiply test") {
        it("10 * 5는 50이 되어야 한다.") {
            calculator.multiply(10, 5) shouldBe 50
        }
    }

    describe("divide test") {
        context("10을 5로 나누면") {
            it("2가 되어야 한다.") {
                val result = calculator.divide(10, 5)
                result shouldBe 2
            }
        }

        context("10을 0으로 나누면") {
            it("에러가 발생한다.") {
                val exception = shouldThrow<ArithmeticException> {
                    calculator.divide(10, 0)
                }
                exception.message shouldBe "/ by zero"
            }
        }
    }
})

```

### Should, Fun

- 테스트 대상이 단순하여 조건이 크게 필요하지 않은 경우 간단히 테스트를 작성하기에 유용.

CalculatorShouldTest.kt

```kotlin
class CalculatorShouldTest : ShouldSpec({
    val calculator = Calculator()

    // without context
    should("10 + 5는 15가 되어야 한다.") {
        calculator.add(10, 5) shouldBe 15
    }

    // with context
    context("divide test") {
        should("10을 5로 나누면 2가 되어야 한다.") {
            calculator.divide(10, 2) shouldBe 2
        }

        should("0으로 나누면 에러가 발생하야 한다.") {
            val exception = shouldThrow<ArithmeticException> {
                calculator.divide(10, 0)
            }
            exception.message shouldBe "/ by zero"
        }
    }
})
```

CalculatorFunTest.kt

```kotlin
class CalculatorFunTest : FunSpec({
    val calculator = Calculator()
    
    // without context
    test("10 + 5는 15가 되어야 한다.") {
        calculator.add(10, 5) shouldBe 15
    }
    
    // with context
    context("divide test") {
        test("10을 5로 나누면 2가 되어야 한다.") {
            calculator.divide(10, 5) shouldBe 2
        }
        
        test("0으로 나누면 에러가 발생해야 한다.") {
            val exception = shouldThrow<ArithmeticException> {
                calculator.divide(10, 0)
            }
            exception.message shouldBe "/ by zero"
        }
    }
})
```

### Annotation

- JUnit과 매우 유사한 형태로 테스트를 할 수 있어 JUnit 테스트를 kotest로 마이그레이션 할 때 유용하게 사용할 수 있음.

```kotlin
class CalculatorAnnotationTest : AnnotationSpec() {
    private val calculator = Calculator()

    @Test
    fun testAdd() {
        calculator.add(10, 5) shouldBe 15
    }

    @Test
    fun testDivideNormalCase() {
        calculator.divide(10, 5) shouldBe 2
    }

    @Test
    fun testDivideByZeroCase() {
        val exception = shouldThrow<ArithmeticException> {
            calculator.divide(10, 0)
        }
        exception.message shouldBe "/ by zero"
    }
}

```

## spring

> Spring이 관리하는 클래스가 포함된 테스트 케이스를 작성할 때의 예제
> 

```kotlin
class SpringTestServiceTest(
    // 빈을 mock 하기 위해 @MockkBean을 선언. @Mockk와 동일한 argument 사용 가능.
    @MockkBean(relaex = true) private val mockSpringTestComponent: SpringTestComponentInterface,
    // 테스트 subject를 주입 받음.
    @Autowired private val subject: SpringTestService,
) : DescribeSpec({

    describe("함수들이 다 잘 동작할 때,") {
        it("빈을 Mock해서 값을 주입할 수 있음") {
            every { mockSpringTestComponent.doWork() } returns "test values"
            // doWork()는 Mocking 되어 주입된다.
            subject.doWorkByTestComponent() shouldBe "test values"
            // relax = true에 의해 test component에서 mock 하지 않은 함수는 empty string을 리턴함.
            subject.doOtherThingsByTestComponent() shouldBe ""
        }
    }
})
```

## spring-webflux
```kotlin
@SpringBootTest
@AutoConfigureWebTestClient
class GreetingControllerTest(
    @MockkBean private val mockGreetingService: GreetingService,
    private val webTestClient: WebTestClient
) : ShouldSpec({

    should("return the greeting provided by greeting service") {
        val greeting = Greeting("Welcome someone")

        every { mockGreetingService.greetingFor("someone") } returns Mono.just(greeting)

        webTestClient
            .get()
            .uri("/greet/someone")
            .exchange()
            .expectStatus().isOk
            .expectBody<Greeting>().isEqualTo(greeting)
    }

    should("return a default greeting when greeting service return error") {
        val defaultGreeting = Greeting("This is default greeting.")

        every { mockGreetingService.greetingFor("someone") } returns Mono.error(RuntimeException("error"))

        webTestClient
            .get()
            .uri("/greet/someone")
            .exchange()
            .expectStatus()
            .isOk()
            .expectBody<Greeting>().isEqualTo(defaultGreeting)
    }
})

```
