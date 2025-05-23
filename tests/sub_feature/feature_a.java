import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.assertEquals;

public class CalculatorTest {
    
    @Test
    void testAdd() {
        Calculator calculator = new Calculator();
        int result = calculator.add(5, 3);
        assertEquals(8, result, "5 + 3 = 8");
    }
    
    @Test
    void testDivide()
    {
        Calculator calculator = new Calculator();
        int result = calculator.divide(10, 2);
        assertEquals(5, result, "10 / 2 = 5");
    }
}


class Calculator {
    public int add(int a, int b) { return a + b; }
    public int divide(int a, int b) { return a / b; }
}


@Test
class NewCalculatorTest {
    void testNewAdd() {
        Calculator calculator = new Calculator();
        int result = calculator.add(15, 23);
        assertEquals(38, result, "15 + 23 = 38");
    }
    
    void testNewDivide() {
        Calculator calculator = new Calculator();
        int result = calculator.divide(40, 2);
        assertEquals(20, result, "40 / 2 = 20");
    }
}
